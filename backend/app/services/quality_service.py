"""
对话质检服务模块
提供自动质检、规则管理、质检报告生成等功能
"""

import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.models import (
    QualityInspection, QualityRule, Conversation, Message, User
)
from app.core.feishu_service import feishu_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityInspectionEngine:
    """质检引擎 - 执行自动质检规则"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rules: List[QualityRule] = []
        self._load_active_rules()
    
    def _load_active_rules(self):
        """加载所有启用的质检规则"""
        self.rules = self.db.query(QualityRule).filter(
            QualityRule.is_active == True
        ).all()
        logger.info(f"Loaded {len(self.rules)} active quality rules")
    
    def inspect_message(self, message: Message, conversation: Conversation) -> QualityInspection:
        """
        对单条消息进行质检
        
        Args:
            message: 需要质检的消息
            conversation: 所属对话
            
        Returns:
            QualityInspection: 质检结果记录
        """
        inspection = QualityInspection(
            conversation_id=conversation.id,
            message_id=message.id,
            inspection_type='auto',
            response_time_seconds=0.0,
            keywords_detected='[]',
            quality_score=100,  # 默认满分
            has_issues=False,
            issues_found='[]'
        )
        
        issues = []
        keywords_found = []
        total_score = 100
        
        # 获取该消息的前一条消息（用于计算响应时间）
        previous_message = self.db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.created_at < message.created_at,
            Message.role == 'user'
        ).order_by(Message.created_at.desc()).first()
        
        # 计算响应时间
        if previous_message and message.role == 'assistant':
            response_time = (message.created_at - previous_message.created_at).total_seconds()
            inspection.response_time_seconds = response_time
            
            # 检查响应时间规则
            for rule in self.rules:
                if rule.rule_type == 'response_time':
                    condition = json.loads(rule.condition)
                    threshold = condition.get('threshold', 10)
                    operator = condition.get('operator', '>')
                    
                    if operator == '>' and response_time > threshold:
                        issues.append({
                            'rule_id': rule.id,
                            'rule_name': rule.rule_name,
                            'issue_type': 'slow_response',
                            'details': f'响应时间过长: {response_time:.2f}秒 (阈值: {threshold}秒)',
                            'severity': 'warning'
                        })
                        total_score += rule.score_impact
        
        # 检查内容规则（仅针对助手回复）
        if message.role == 'assistant':
            content = message.content
            
            for rule in self.rules:
                condition = json.loads(rule.condition)
                
                # 关键词检测
                if rule.rule_type == 'keywords':
                    keywords = condition.get('keywords', [])
                    match_type = condition.get('match_type', 'any')  # any, all
                    
                    matched = []
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            matched.append(keyword)
                    
                    if match_type == 'any' and matched:
                        keywords_found.extend(matched)
                    elif match_type == 'all' and len(matched) == len(keywords):
                        keywords_found.extend(matched)
                
                # 回复长度检测
                elif rule.rule_type == 'length':
                    min_length = condition.get('min_length', 0)
                    max_length = condition.get('max_length', 10000)
                    content_length = len(content)
                    
                    if content_length < min_length:
                        issues.append({
                            'rule_id': rule.id,
                            'rule_name': rule.rule_name,
                            'issue_type': 'too_short',
                            'details': f'回复过短: {content_length}字符 (最小: {min_length})',
                            'severity': 'info'
                        })
                        total_score += rule.score_impact
                    elif content_length > max_length:
                        issues.append({
                            'rule_id': rule.id,
                            'rule_name': rule.rule_name,
                            'issue_type': 'too_long',
                            'details': f'回复过长: {content_length}字符 (最大: {max_length})',
                            'severity': 'warning'
                        })
                        total_score += rule.score_impact
                
                # 敏感词检测
                elif rule.rule_type == 'sensitive_words':
                    sensitive_words = condition.get('words', [])
                    found_sensitive = []
                    
                    for word in sensitive_words:
                        if word.lower() in content.lower():
                            found_sensitive.append(word)
                    
                    if found_sensitive:
                        issues.append({
                            'rule_id': rule.id,
                            'rule_name': rule.rule_name,
                            'issue_type': 'sensitive_content',
                            'details': f'检测到敏感词: {", ".join(found_sensitive)}',
                            'severity': 'critical'
                        })
                        total_score += rule.score_impact
                
                # 格式检测
                elif rule.rule_type == 'format':
                    required_elements = condition.get('required_elements', [])
                    for element in required_elements:
                        if element == 'greeting' and not self._has_greeting(content):
                            issues.append({
                                'rule_id': rule.id,
                                'rule_name': rule.rule_name,
                                'issue_type': 'missing_greeting',
                                'details': '缺少问候语',
                                'severity': 'info'
                            })
                            total_score += rule.score_impact
                        elif element == 'signature' and not self._has_signature(content):
                            issues.append({
                                'rule_id': rule.id,
                                'rule_name': rule.rule_name,
                                'issue_type': 'missing_signature',
                                'details': '缺少署名/结束语',
                                'severity': 'info'
                            })
                            total_score += rule.score_impact
        
        # 更新质检结果
        inspection.quality_score = max(0, min(100, total_score))
        inspection.has_issues = len(issues) > 0
        inspection.issues_found = json.dumps(issues, ensure_ascii=False)
        inspection.keywords_detected = json.dumps(list(set(keywords_found)), ensure_ascii=False)
        
        return inspection
    
    def _has_greeting(self, content: str) -> bool:
        """检查是否包含问候语"""
        greetings = ['你好', '您好', 'Hi', 'Hello', '欢迎', '感谢', '谢谢']
        return any(g.lower() in content.lower() for g in greetings)
    
    def _has_signature(self, content: str) -> bool:
        """检查是否包含署名/结束语"""
        signatures = ['祝好', '谢谢', '感谢', '再见', 'best', 'regards', '客服']
        return any(s.lower() in content.lower() for s in signatures)
    
    def inspect_conversation(self, conversation_id: UUID) -> List[QualityInspection]:
        """
        对整个对话进行质检
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            List[QualityInspection]: 所有消息的质检结果
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return []
            
            # 获取所有助手回复
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id,
                Message.role == 'assistant'
            ).order_by(Message.created_at.asc()).all()
            
            inspections = []
            for message in messages:
                inspection = self.inspect_message(message, conversation)
                inspections.append(inspection)
                self.db.add(inspection)
            
            self.db.commit()
            logger.info(f"Inspected {len(inspections)} messages for conversation {conversation_id}")
            
            # 发送飞书推送（异步）
            self._send_feishu_notification(conversation_id, inspections)
            
            return inspections
            
        except Exception as e:
            logger.error(f"Quality inspection failed for conversation {conversation_id}", error=str(e))
            self.db.rollback()
            return []
    
    async def inspect_conversation_async(self, conversation_id: UUID) -> List[QualityInspection]:
        """
        异步版本：对整个对话进行质检
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            List[QualityInspection]: 所有消息的质检结果
        """
        return self.inspect_conversation(conversation_id)
    
    def _send_feishu_notification(self, conversation_id: UUID, inspections: List[QualityInspection]):
        """
        发送质检问题飞书推送
        
        Args:
            conversation_id: 对话ID
            inspections: 质检结果列表
        """
        try:
            # 检查是否有严重问题
            critical_issues = [
                ins for ins in inspections 
                if ins.has_issues and any(
                    issue.get('severity') == 'critical' 
                    for issue in json.loads(ins.issues_found)
                )
            ]
            
            # 总体质量问题（低分）
            avg_score = sum(ins.quality_score for ins in inspections) / len(inspections) if inspections else 0
            has_low_score = avg_score < 70
            
            if critical_issues or has_low_score:
                # 异步发送飞书通知（不阻塞主流程）
                asyncio.create_task(self._async_send_feishu_alert(
                    conversation_id=conversation_id,
                    inspections=inspections,
                    avg_score=avg_score,
                    critical_count=len(critical_issues)
                ))
        except Exception as e:
            logger.warning(f"Failed to prepare feishu notification", error=str(e))
    
    async def _async_send_feishu_alert(
        self, 
        conversation_id: UUID,
        inspections: List[QualityInspection],
        avg_score: float,
        critical_count: int
    ):
        """
        异步发送飞书告警
        
        Args:
            conversation_id: 对话ID
            inspections: 质检结果列表
            avg_score: 平均分
            critical_count: 严重问题数
        """
        try:
            # 尝试获取对话信息
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            conversation_title = conversation.title if conversation else f"对话 {conversation_id}"
            
            # 构建飞书卡片消息
            title = "🚨 客服质检告警"
            
            content_lines = [
                f"对话标题: {conversation_title}",
                f"质检时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}UTC",
                f"平均质量分: {avg_score:.1f}/100",
                f"严重问题数: {critical_count}",
                "",
                "问题详情:"
            ]
            
            # 列出前3个最严重的问题
            issues_by_severity = []
            for ins in inspections:
                if ins.has_issues:
                    for issue in json.loads(ins.issues_found):
                        severity = issue.get('severity', 'info')
                        issues_by_severity.append({
                            'severity': severity,
                            'type': issue.get('issue_type', 'unknown'),
                            'details': issue.get('details', ''),
                            'score': ins.quality_score
                        })
            
            # 按严重性排序
            severity_order = {'critical': 0, 'warning': 1, 'info': 2}
            issues_by_severity.sort(key=lambda x: severity_order.get(x['severity'], 3))
            
            for i, issue in enumerate(issues_by_severity[:5], 1):  # 只显示前5个
                emoji = "🔴" if issue['severity'] == 'critical' else "🟡" if issue['severity'] == 'warning' else "🔵"
                content_lines.append(f"{emoji} {issue['type']}: {issue['details']}")
            
            content = "\n".join(content_lines)
            
            # 发送飞书卡片
            success = await feishu_service.send_card(
                title=title,
                content=content,
                theme_color="red" if critical_count > 0 else "orange",
                fields=[
                    {"title": "对话ID", "value": str(conversation_id)[:20] + "..."},
                    {"title": "质检消息数", "value": str(len(inspections))},
                    {"title": "平均质量分", "value": f"{avg_score:.1f}"},
                    {"title": "严重问题数", "value": str(critical_count)}
                ],
                button_text="查看对话详情",
                button_url=f"http://your-admin-server/admin/conversations/{conversation_id}"  # TODO: 替换为实际管理后台URL
            )
            
            if success:
                logger.info("Quality alert sent to Feishu", 
                          conversation_id=conversation_id,
                          avg_score=avg_score,
                          critical_count=critical_count)
            else:
                logger.warning("Failed to send quality alert to Feishu")
                
        except Exception as e:
            logger.error("Error sending feishu quality alert", error=str(e))


class QualityReportService:
    """质检报告服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        生成每日质检报告
        
        Args:
            date: 报告日期，默认为昨天
            
        Returns:
            Dict: 质检报告数据
        """
        if date is None:
            date = datetime.utcnow() - timedelta(days=1)
        
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # 查询当天的质检记录
        inspections = self.db.query(QualityInspection).filter(
            QualityInspection.created_at >= start_time,
            QualityInspection.created_at < end_time
        ).all()
        
        if not inspections:
            return {
                'date': start_time.strftime('%Y-%m-%d'),
                'total_inspected': 0,
                'message': '当日无质检记录'
            }
        
        # 统计指标
        total_inspected = len(inspections)
        avg_score = sum(i.quality_score for i in inspections) / total_inspected
        issues_count = sum(1 for i in inspections if i.has_issues)
        issues_rate = (issues_count / total_inspected) * 100
        
        # 问题分类统计
        issue_types = {}
        for inspection in inspections:
            issues = json.loads(inspection.issues_found)
            for issue in issues:
                issue_type = issue.get('issue_type', 'unknown')
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        # 低分对话（分数<60）
        low_score_inspections = [
            {
                'conversation_id': str(i.conversation_id),
                'message_id': str(i.message_id) if i.message_id else None,
                'score': i.quality_score,
                'issues': json.loads(i.issues_found)
            }
            for i in inspections if i.quality_score < 60
        ]
        
        # 响应时间统计
        response_times = [i.response_time_seconds for i in inspections if i.response_time_seconds > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        report = {
            'date': start_time.strftime('%Y-%m-%d'),
            'total_inspected': total_inspected,
            'average_score': round(avg_score, 2),
            'issues_count': issues_count,
            'issues_rate': round(issues_rate, 2),
            'average_response_time': round(avg_response_time, 2),
            'issue_breakdown': issue_types,
            'low_score_conversations': low_score_inspections[:10],  # 只返回前10个
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
    
    def generate_conversation_report(self, conversation_id: UUID) -> Dict[str, Any]:
        """
        生成单个对话的质检报告
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Dict: 对话质检详情
        """
        inspections = self.db.query(QualityInspection).filter(
            QualityInspection.conversation_id == conversation_id
        ).order_by(QualityInspection.created_at.asc()).all()
        
        if not inspections:
            return {
                'conversation_id': str(conversation_id),
                'message': '该对话暂无质检记录'
            }
        
        avg_score = sum(i.quality_score for i in inspections) / len(inspections)
        
        messages_detail = []
        for inspection in inspections:
            message = self.db.query(Message).filter(
                Message.id == inspection.message_id
            ).first()
            
            messages_detail.append({
                'message_id': str(inspection.message_id),
                'score': inspection.quality_score,
                'has_issues': inspection.has_issues,
                'response_time': inspection.response_time_seconds,
                'issues': json.loads(inspection.issues_found),
                'content_preview': message.content[:100] + '...' if message and len(message.content) > 100 else (message.content if message else '')
            })
        
        return {
            'conversation_id': str(conversation_id),
            'total_messages': len(inspections),
            'average_score': round(avg_score, 2),
            'messages': messages_detail
        }
    
    def get_quality_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取质检趋势数据
        
        Args:
            days: 查询天数
            
        Returns:
            List[Dict]: 每日质检统计数据
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计
        results = self.db.query(
            func.date(QualityInspection.created_at).label('date'),
            func.count(QualityInspection.id).label('total'),
            func.avg(QualityInspection.quality_score).label('avg_score'),
            func.sum(QualityInspection.has_issues.cast(Integer)).label('issues_count')
        ).filter(
            QualityInspection.created_at >= start_date
        ).group_by(
            func.date(QualityInspection.created_at)
        ).order_by(
            func.date(QualityInspection.created_at)
        ).all()
        
        trends = []
        for row in results:
            trends.append({
                'date': row.date.strftime('%Y-%m-%d'),
                'total_inspected': row.total,
                'average_score': round(float(row.avg_score or 0), 2),
                'issues_count': int(row.issues_count or 0),
                'issues_rate': round((row.issues_count / row.total * 100) if row.total > 0 else 0, 2)
            })
        
        return trends


class QualityRuleService:
    """质检规则管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: Dict[str, Any]) -> QualityRule:
        """创建新规则"""
        rule = QualityRule(
            rule_name=rule_data['rule_name'],
            rule_type=rule_data['rule_type'],
            condition=json.dumps(rule_data['condition'], ensure_ascii=False),
            score_impact=rule_data.get('score_impact', 0),
            is_active=rule_data.get('is_active', True)
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"Created quality rule: {rule.rule_name}")
        return rule
    
    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> Optional[QualityRule]:
        """更新规则"""
        rule = self.db.query(QualityRule).filter(QualityRule.id == rule_id).first()
        if not rule:
            return None
        
        if 'rule_name' in rule_data:
            rule.rule_name = rule_data['rule_name']
        if 'rule_type' in rule_data:
            rule.rule_type = rule_data['rule_type']
        if 'condition' in rule_data:
            rule.condition = json.dumps(rule_data['condition'], ensure_ascii=False)
        if 'score_impact' in rule_data:
            rule.score_impact = rule_data['score_impact']
        if 'is_active' in rule_data:
            rule.is_active = rule_data['is_active']
        
        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"Updated quality rule: {rule.rule_name}")
        return rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        rule = self.db.query(QualityRule).filter(QualityRule.id == rule_id).first()
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        logger.info(f"Deleted quality rule: {rule.rule_name}")
        return True
    
    def get_rules(self, active_only: bool = False) -> List[QualityRule]:
        """获取规则列表"""
        query = self.db.query(QualityRule)
        if active_only:
            query = query.filter(QualityRule.is_active == True)
        return query.order_by(QualityRule.created_at.desc()).all()
    
    def get_rule(self, rule_id: int) -> Optional[QualityRule]:
        """获取单个规则"""
        return self.db.query(QualityRule).filter(QualityRule.id == rule_id).first()
    
    def init_default_rules(self):
        """初始化默认质检规则"""
        default_rules = [
            {
                'rule_name': '响应时间检测',
                'rule_type': 'response_time',
                'condition': {'threshold': 10, 'operator': '>'},
                'score_impact': -10
            },
            {
                'rule_name': '回复长度检测',
                'rule_type': 'length',
                'condition': {'min_length': 10, 'max_length': 2000},
                'score_impact': -5
            },
            {
                'rule_name': '问候语检测',
                'rule_type': 'format',
                'condition': {'required_elements': ['greeting']},
                'score_impact': -3
            },
            {
                'rule_name': '结束语检测',
                'rule_type': 'format',
                'condition': {'required_elements': ['signature']},
                'score_impact': -3
            }
        ]
        
        created_count = 0
        for rule_data in default_rules:
            # 检查是否已存在同名规则
            existing = self.db.query(QualityRule).filter(
                QualityRule.rule_name == rule_data['rule_name']
            ).first()
            
            if not existing:
                self.create_rule(rule_data)
                created_count += 1
        
        logger.info(f"Initialized {created_count} default quality rules")
        return created_count


# 初始化默认规则的便捷函数
def init_quality_rules(db: Session) -> int:
    """初始化默认质检规则"""
    service = QualityRuleService(db)
    return service.init_default_rules()


def inspect_conversation(db: Session, conversation_id: UUID) -> List[QualityInspection]:
    """对对话进行质检的便捷函数"""
    engine = QualityInspectionEngine(db)
    return engine.inspect_conversation(conversation_id)


def generate_daily_report(db: Session, date: Optional[datetime] = None) -> Dict[str, Any]:
    """生成每日报告的便捷函数"""
    service = QualityReportService(db)
    return service.generate_daily_report(date)