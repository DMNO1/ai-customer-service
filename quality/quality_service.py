"""
质检服务 (Quality Service)

提供对话质检的核心服务，包括对话分析、报告生成、批量质检等功能。
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

from .quality_report import QualityReport, ConversationMetrics, QualityStatus, QualityReportCollection
from .analyzer import ConversationAnalyzer, Message


class QualityService:
    """质检服务"""
    
    # 默认敏感词列表
    DEFAULT_SENSITIVE_WORDS = [
        "投诉", "举报", "差评", "退款", "骗子", "欺诈",
        "垃圾", "恶心", "太差", "烂", "坑人", "上当",
        "虚假宣传", "欺骗", "忽悠", "不靠谱"
    ]
    
    # 响应超时阈值（秒）
    TIMEOUT_THRESHOLD = 30
    
    def __init__(self, sensitive_words: Optional[List[str]] = None, 
                 storage_path: Optional[str] = None):
        """
        初始化质检服务
        
        Args:
            sensitive_words: 自定义敏感词列表
            storage_path: 报告存储路径
        """
        self.sensitive_words = sensitive_words or self.DEFAULT_SENSITIVE_WORDS
        self.analyzer = ConversationAnalyzer(self.sensitive_words)
        self.storage_path = Path(storage_path) if storage_path else Path("./quality_reports")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 报告集合
        self.report_collection = QualityReportCollection()
    
    async def analyze_conversation(self, conversation_id: str, 
                                   messages: List[Dict[str, Any]]) -> QualityReport:
        """
        分析单个对话质量
        
        Args:
            conversation_id: 对话ID
            messages: 消息列表，格式为 [{"id": str, "role": str, "content": str, "created_at": str}, ...]
            
        Returns:
            质检报告
        """
        # 转换消息格式
        message_objects = []
        for msg in messages:
            created_at = msg.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            elif not isinstance(created_at, datetime):
                created_at = datetime.now()
            
            message_objects.append(Message(
                id=msg.get("id", str(uuid.uuid4())),
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                created_at=created_at,
                metadata=msg.get("metadata")
            ))
        
        # 进行全面分析
        analysis_result = self.analyzer.analyze_conversation(message_objects)
        
        # 创建指标对象
        metrics = ConversationMetrics(
            avg_response_time=analysis_result["response_time"]["avg_response_time"],
            max_response_time=analysis_result["response_time"]["max_response_time"],
            timeout_count=analysis_result["response_time"]["timeout_count"],
            message_count=analysis_result["message_stats"]["total"],
            user_message_count=analysis_result["message_stats"]["user"],
            ai_message_count=analysis_result["message_stats"]["assistant"],
            sensitive_words=analysis_result["sensitive_words"]["words"],
            sensitive_word_count=analysis_result["sensitive_words"]["count"],
            is_complete=analysis_result["completeness"]["is_complete"],
            has_greeting=analysis_result["completeness"]["has_greeting"],
            has_farewell=analysis_result["completeness"]["has_farewell"]
        )
        
        # 创建报告
        report = QualityReport(
            report_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            score=analysis_result["score"],
            metrics=metrics
        )
        
        # 根据分数设置状态
        report.set_status_from_score()
        
        # 添加检测到的问题
        if analysis_result["sensitive_words"]["detected"]:
            for location in analysis_result["sensitive_words"]["locations"]:
                report.add_issue(
                    category="sensitive_content",
                    severity="high" if location["role"] == "assistant" else "medium",
                    description=f"检测到敏感词: {location['word']}",
                    details=location
                )
        
        if analysis_result["response_time"]["timeout_count"] > 0:
            report.add_issue(
                category="response_time",
                severity="medium",
                description=f"检测到 {analysis_result['response_time']['timeout_count']} 次响应超时",
                details={
                    "timeout_count": analysis_result["response_time"]["timeout_count"],
                    "avg_response_time": analysis_result["response_time"]["avg_response_time"]
                }
            )
        
        if not analysis_result["completeness"]["is_complete"]:
            report.add_issue(
                category="completeness",
                severity="low",
                description="对话可能未完成，最后一条消息是用户发送的",
                details={"last_message_role": analysis_result["completeness"]["last_message_role"]}
            )
        
        # 添加建议
        if analysis_result["sentiment"]["sentiment"] == "negative":
            report.add_suggestion("用户情绪偏负面，建议关注用户反馈并改进服务质量")
        
        if not analysis_result["completeness"]["has_greeting"]:
            report.add_suggestion("建议在对话开始时添加问候语，提升用户体验")
        
        if not analysis_result["completeness"]["has_farewell"]:
            report.add_suggestion("建议在对话结束时添加结束语，保持服务完整性")
        
        if analysis_result["response_time"]["avg_response_time"] > 10:
            report.add_suggestion("响应时间较长，建议优化AI响应速度")
        
        # 保存报告
        self._save_report(report)
        self.report_collection.add_report(report)
        
        return report
    
    def _save_report(self, report: QualityReport):
        """保存报告到文件"""
        report_file = self.storage_path / f"{report.report_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_report(self, report_id: str) -> Optional[QualityReport]:
        """获取报告"""
        # 先从内存中查找
        for report in self.report_collection.reports:
            if report.report_id == report_id:
                return report
        
        # 从文件加载
        report_file = self.storage_path / f"{report_id}.json"
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 这里简化处理，实际应该完整重建对象
                return None
        
        return None
    
    def get_conversation_report(self, conversation_id: str) -> Optional[QualityReport]:
        """获取指定对话的质检报告"""
        for report in self.report_collection.reports:
            if report.conversation_id == conversation_id:
                return report
        return None
    
    def get_summary(self, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取质检汇总统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            汇总统计
        """
        reports = self.report_collection.reports
        
        # 过滤日期范围
        if start_date or end_date:
            filtered_reports = []
            for report in reports:
                if start_date and report.checked_at < start_date:
                    continue
                if end_date and report.checked_at > end_date:
                    continue
                filtered_reports.append(report)
            reports = filtered_reports
        
        if not reports:
            return {
                "total": 0,
                "pass_count": 0,
                "fail_count": 0,
                "warning_count": 0,
                "avg_score": 0.0,
                "pass_rate": 0.0
            }
        
        total = len(reports)
        pass_count = sum(1 for r in reports if r.status == QualityStatus.PASS)
        fail_count = sum(1 for r in reports if r.status == QualityStatus.FAIL)
        warning_count = sum(1 for r in reports if r.status == QualityStatus.WARNING)
        avg_score = sum(r.score for r in reports) / total
        
        return {
            "total": total,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "warning_count": warning_count,
            "avg_score": round(avg_score, 2),
            "pass_rate": round(pass_count / total * 100, 2)
        }
    
    def get_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取质检趋势
        
        Args:
            days: 天数
            
        Returns:
            趋势数据
        """
        trend = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 统计当天的报告
            day_reports = [
                r for r in self.report_collection.reports
                if current_date <= r.checked_at < next_date
            ]
            
            if day_reports:
                avg_score = sum(r.score for r in day_reports) / len(day_reports)
                trend.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "count": len(day_reports),
                    "avg_score": round(avg_score, 2)
                })
            else:
                trend.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "count": 0,
                    "avg_score": 0.0
                })
            
            current_date = next_date
        
        return trend
    
    def export_report(self, report_id: str, format: str = "json") -> Optional[str]:
        """
        导出报告
        
        Args:
            report_id: 报告ID
            format: 导出格式 (json, html)
            
        Returns:
            导出文件路径
        """
        report = self.get_report(report_id)
        if not report:
            return None
        
        if format == "json":
            export_path = self.storage_path / "exports" / f"{report_id}.json"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
            return str(export_path)
        
        elif format == "html":
            export_path = self.storage_path / "exports" / f"{report_id}.html"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成简单的HTML报告
            html_content = self._generate_html_report(report)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return str(export_path)
        
        return None
    
    def _generate_html_report(self, report: QualityReport) -> str:
        """生成HTML格式报告"""
        status_colors = {
            QualityStatus.PASS: "#10B981",
            QualityStatus.FAIL: "#EF4444",
            QualityStatus.WARNING: "#F59E0B",
            QualityStatus.PENDING: "#6B7280"
        }
        
        status_labels = {
            QualityStatus.PASS: "通过",
            QualityStatus.FAIL: "不通过",
            QualityStatus.WARNING: "警告",
            QualityStatus.PENDING: "待检查"
        }
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>对话质检报告 - {report.conversation_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        .status {{ display: inline-block; padding: 6px 12px; border-radius: 4px; color: white; font-weight: bold; }}
        .score {{ font-size: 48px; font-weight: bold; color: {status_colors[report.status]}; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 6px; }}
        .section h3 {{ margin-top: 0; color: #374151; }}
        .metric {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
        .issue {{ padding: 10px; margin: 8px 0; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 4px; }}
        .suggestion {{ padding: 10px; margin: 8px 0; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>对话质检报告</h1>
        
        <div style="text-align: center; margin: 30px 0;">
            <div class="score">{report.score}</div>
            <div style="color: #6b7280;">综合评分</div>
            <div class="status" style="background: {status_colors[report.status]}; margin-top: 10px;">
                {status_labels[report.status]}
            </div>
        </div>
        
        <div class="section">
            <h3>基本信息</h3>
            <div class="metric"><span>报告ID:</span><span>{report.report_id}</span></div>
            <div class="metric"><span>对话ID:</span><span>{report.conversation_id}</span></div>
            <div class="metric"><span>检查时间:</span><span>{report.checked_at.strftime('%Y-%m-%d %H:%M:%S')}</span></div>
        </div>
        
        <div class="section">
            <h3>指标详情</h3>
            <div class="metric"><span>平均响应时间:</span><span>{report.metrics.avg_response_time:.2f}秒</span></div>
            <div class="metric"><span>超时次数:</span><span>{report.metrics.timeout_count}</span></div>
            <div class="metric"><span>消息总数:</span><span>{report.metrics.message_count}</span></div>
            <div class="metric"><span>敏感词数量:</span><span>{report.metrics.sensitive_word_count}</span></div>
            <div class="metric"><span>对话完成:</span><span>{'是' if report.metrics.is_complete else '否'}</span></div>
        </div>
        
        {"<div class='section'><h3>检测到的问题</h3>" + "".join([f"<div class='issue'><strong>{issue['category']}</strong> - {issue['description']}</div>" for issue in report.issues]) + "</div>" if report.issues else ""}
        
        {"<div class='section'><h3>改进建议</h3>" + "".join([f"<div class='suggestion'>{suggestion}</div>" for suggestion in report.suggestions]) + "</div>" if report.suggestions else ""}
    </div>
</body>
</html>
"""
        return html
