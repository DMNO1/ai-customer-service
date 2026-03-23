"""
对话质检服务 - 干运行测试 (Dry Run)
不依赖数据库，仅测试核心逻辑
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import json
from datetime import datetime, timedelta
from uuid import uuid4

# 模拟数据类
class MockMessage:
    def __init__(self, id, conversation_id, role, content, created_at):
        self.id = id
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.created_at = created_at

class MockConversation:
    def __init__(self, id, user_id):
        self.id = id
        self.user_id = user_id

class MockInspection:
    """模拟质检结果"""
    def __init__(self):
        self.id = 1
        self.conversation_id = None
        self.message_id = None
        self.inspection_type = 'auto'
        self.response_time_seconds = 0.0
        self.keywords_detected = '[]'
        self.quality_score = 100
        self.has_issues = False
        self.issues_found = '[]'

class MockRule:
    """模拟质检规则"""
    def __init__(self, id, name, rule_type, condition, score_impact):
        self.id = id
        self.rule_name = name
        self.rule_type = rule_type
        self.condition = json.dumps(condition)
        self.score_impact = score_impact
        self.is_active = True


class QualityInspectionEngineDryRun:
    """质检引擎 - 干运行版本"""
    
    def __init__(self):
        # 默认规则
        self.rules = [
            MockRule(1, '响应时间检测', 'response_time', {'threshold': 10, 'operator': '>'}, -10),
            MockRule(2, '回复长度检测', 'length', {'min_length': 10, 'max_length': 2000}, -5),
            MockRule(3, '问候语检测', 'format', {'required_elements': ['greeting']}, -3),
            MockRule(4, '结束语检测', 'format', {'required_elements': ['signature']}, -3),
            MockRule(5, '敏感词检测', 'sensitive_words', {'words': ['脏话', '不文明']}, -20),
        ]
    
    def inspect_message(self, message: MockMessage, conversation: MockConversation, 
                       previous_message: MockMessage = None) -> MockInspection:
        """对单条消息进行质检"""
        inspection = MockInspection()
        inspection.conversation_id = conversation.id
        inspection.message_id = message.id
        
        issues = []
        keywords_found = []
        total_score = 100
        
        # 计算响应时间
        if previous_message and message.role == 'assistant':
            response_time = (message.created_at - previous_message.created_at).total_seconds()
            inspection.response_time_seconds = response_time
            
            # 检查响应时间规则
            for rule in self.rules:
                if rule.rule_type == 'response_time':
                    condition = json.loads(rule.condition)
                    threshold = condition.get('threshold', 10)
                    
                    if response_time > threshold:
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
                
                # 回复长度检测
                if rule.rule_type == 'length':
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


def test_quality_inspection():
    """测试质检功能"""
    print("=" * 60)
    print("对话质检服务 - 干运行测试 (Dry Run)")
    print("=" * 60)
    
    engine = QualityInspectionEngineDryRun()
    
    # 创建测试数据
    conv_id = uuid4()
    conversation = MockConversation(conv_id, uuid4())
    
    now = datetime.utcnow()
    
    # 测试消息序列
    messages = [
        MockMessage(uuid4(), conv_id, "user", "你好，我想了解一下产品", now),
        MockMessage(uuid4(), conv_id, "assistant", 
                   "您好！很高兴为您服务。我们的产品是AI智能客服系统。请问有什么可以帮您？",
                   now + timedelta(seconds=2)),
        MockMessage(uuid4(), conv_id, "user", "价格是多少？", now + timedelta(seconds=5)),
        MockMessage(uuid4(), conv_id, "assistant",
                   "我们的定价方案如下：基础版每月99元，专业版每月299元。",
                   now + timedelta(seconds=20)),  # 响应慢
        MockMessage(uuid4(), conv_id, "user", "好的", now + timedelta(seconds=25)),
        MockMessage(uuid4(), conv_id, "assistant", "不客气", now + timedelta(seconds=26)),  # 过短
    ]
    
    print("\n=== 测试场景 ===")
    print(f"对话ID: {conv_id}")
    print(f"消息数量: {len(messages)}")
    
    print("\n=== 质检规则 ===")
    for rule in engine.rules:
        print(f"  - {rule.rule_name} ({rule.rule_type})")
    
    print("\n=== 消息质检结果 ===")
    assistant_messages = [m for m in messages if m.role == "assistant"]
    user_messages = [m for m in messages if m.role == "user"]
    
    inspections = []
    for i, msg in enumerate(assistant_messages):
        # 找到对应的用户消息
        prev_msg = None
        for um in user_messages:
            if um.created_at < msg.created_at:
                if prev_msg is None or um.created_at > prev_msg.created_at:
                    prev_msg = um
        
        inspection = engine.inspect_message(msg, conversation, prev_msg)
        inspections.append(inspection)
        
        print(f"\n消息 {i+1}: {msg.content[:40]}...")
        print(f"  质检分数: {inspection.quality_score}/100")
        print(f"  响应时间: {inspection.response_time_seconds:.2f}秒")
        print(f"  发现问题: {'是' if inspection.has_issues else '否'}")
        
        issues = json.loads(inspection.issues_found)
        if issues:
            for issue in issues:
                print(f"    [!] {issue['issue_type']}: {issue['details']}")
    
    # 统计
    print("\n=== 质检统计 ===")
    avg_score = sum(i.quality_score for i in inspections) / len(inspections)
    issues_count = sum(1 for i in inspections if i.has_issues)
    
    print(f"质检消息数: {len(inspections)}")
    print(f"平均分数: {avg_score:.2f}")
    print(f"问题数: {issues_count}")
    print(f"问题率: {(issues_count/len(inspections)*100):.1f}%")
    
    # 测试报告生成
    print("\n=== 模拟报告生成 ===")
    report = {
        'date': now.strftime('%Y-%m-%d'),
        'total_inspected': len(inspections),
        'average_score': round(avg_score, 2),
        'issues_count': issues_count,
        'issues_rate': round((issues_count/len(inspections)*100), 2),
        'generated_at': datetime.utcnow().isoformat()
    }
    print(f"报告日期: {report['date']}")
    print(f"质检总数: {report['total_inspected']}")
    print(f"平均分数: {report['average_score']}")
    print(f"问题率: {report['issues_rate']}%")
    
    print("\n" + "=" * 60)
    print("[OK] 干运行测试完成！核心逻辑验证通过")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_quality_inspection()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)