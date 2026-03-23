"""
对话质检服务测试脚本
测试质检引擎、规则管理和报告生成功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import json
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.models import (
    Base, User, Conversation, Message, QualityInspection, 
    QualityRule, KnowledgeBase
)
from app.services.quality_service import (
    QualityInspectionEngine,
    QualityReportService,
    QualityRuleService,
    init_quality_rules
)

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_quality.db"


def setup_test_db():
    """设置测试数据库"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_test_data(db: Session):
    """创建测试数据"""
    # 创建测试用户
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        role="user"
    )
    db.add(user)
    db.commit()
    
    # 创建知识库
    kb = KnowledgeBase(
        id=uuid4(),
        user_id=user.id,
        name="Test Knowledge Base",
        vector_collection_name="test_collection"
    )
    db.add(kb)
    db.commit()
    
    # 创建测试对话
    conversation = Conversation(
        id=uuid4(),
        user_id=user.id,
        knowledge_base_id=kb.id,
        session_id="test_session_001",
        title="测试对话",
        status="active"
    )
    db.add(conversation)
    db.commit()
    
    # 创建测试消息
    now = datetime.utcnow()
    messages = [
        # 用户消息
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="你好，我想了解一下你们的产品",
            created_at=now
        ),
        # 助手回复 - 正常
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="您好！很高兴为您服务。我们的产品是一款AI智能客服系统，可以帮助企业自动化处理客户咨询。请问您有什么具体问题吗？",
            created_at=now + timedelta(seconds=2)
        ),
        # 用户消息
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="价格是多少？",
            created_at=now + timedelta(seconds=5)
        ),
        # 助手回复 - 响应慢
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="我们的定价方案如下：基础版每月99元，专业版每月299元，企业版需要联系销售。",
            created_at=now + timedelta(seconds=20)  # 响应时间15秒
        ),
        # 用户消息
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="好的，谢谢",
            created_at=now + timedelta(seconds=25)
        ),
        # 助手回复 - 过短
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="不客气",
            created_at=now + timedelta(seconds=26)
        ),
    ]
    
    for msg in messages:
        db.add(msg)
    db.commit()
    
    return conversation.id, user.id


def test_init_default_rules(db: Session):
    """测试初始化默认规则"""
    print("\n=== 测试初始化默认规则 ===")
    count = init_quality_rules(db)
    print(f"✓ 初始化 {count} 条默认规则")
    
    rules = db.query(QualityRule).all()
    print(f"✓ 数据库中共有 {len(rules)} 条规则")
    
    for rule in rules:
        print(f"  - {rule.rule_name} ({rule.rule_type})")
    
    return rules


def test_inspect_message(db: Session, conversation_id: UUID):
    """测试单条消息质检"""
    print("\n=== 测试单条消息质检 ===")
    engine = QualityInspectionEngine(db)
    
    # 获取助手回复
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.role == "assistant"
    ).all()
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    for i, msg in enumerate(messages):
        print(f"\n消息 {i+1}: {msg.content[:50]}...")
        inspection = engine.inspect_message(msg, conversation)
        db.add(inspection)
        print(f"  质检分数: {inspection.quality_score}")
        print(f"  响应时间: {inspection.response_time_seconds:.2f}秒")
        print(f"  发现问题: {inspection.has_issues}")
        
        issues = json.loads(inspection.issues_found)
        if issues:
            for issue in issues:
                print(f"    - {issue['issue_type']}: {issue['details']}")
    
    db.commit()
    print("\n✓ 消息质检完成")


def test_inspect_conversation(db: Session, conversation_id: UUID):
    """测试整对话质检"""
    print("\n=== 测试整对话质检 ===")
    engine = QualityInspectionEngine(db)
    
    inspections = engine.inspect_conversation(conversation_id)
    print(f"✓ 完成 {len(inspections)} 条消息的质检")
    
    for inspection in inspections:
        print(f"  - 分数: {inspection.quality_score}, 问题: {inspection.has_issues}")


def test_generate_reports(db: Session):
    """测试报告生成"""
    print("\n=== 测试报告生成 ===")
    service = QualityReportService(db)
    
    # 每日报告
    print("\n--- 每日质检报告 ---")
    daily_report = service.generate_daily_report()
    print(f"日期: {daily_report['date']}")
    print(f"质检总数: {daily_report['total_inspected']}")
    print(f"平均分数: {daily_report['average_score']}")
    print(f"问题数: {daily_report['issues_count']}")
    print(f"问题率: {daily_report['issues_rate']}%")
    print(f"平均响应时间: {daily_report['average_response_time']}秒")
    print(f"问题分布: {daily_report['issue_breakdown']}")
    
    # 趋势报告
    print("\n--- 质检趋势 (7天) ---")
    trends = service.get_quality_trends(days=7)
    for trend in trends:
        print(f"  {trend['date']}: 平均{trend['average_score']}分, {trend['issues_rate']}%有问题")


def test_rule_management(db: Session):
    """测试规则管理"""
    print("\n=== 测试规则管理 ===")
    service = QualityRuleService(db)
    
    # 创建新规则
    print("\n--- 创建新规则 ---")
    new_rule = service.create_rule({
        'rule_name': '测试规则-敏感词检测',
        'rule_type': 'sensitive_words',
        'condition': {'words': ['脏话', '不文明']},
        'score_impact': -20,
        'is_active': True
    })
    print(f"✓ 创建规则: {new_rule.rule_name} (ID: {new_rule.id})")
    
    # 获取所有规则
    print("\n--- 规则列表 ---")
    rules = service.get_rules()
    for rule in rules:
        print(f"  - {rule.rule_name} ({'启用' if rule.is_active else '禁用'})")
    
    # 更新规则
    print("\n--- 更新规则 ---")
    updated = service.update_rule(new_rule.id, {
        'rule_name': '测试规则-敏感词检测(已更新)',
        'is_active': False
    })
    print(f"✓ 更新规则: {updated.rule_name}")
    
    # 删除规则
    print("\n--- 删除规则 ---")
    success = service.delete_rule(new_rule.id)
    print(f"✓ 删除规则: {'成功' if success else '失败'}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("对话质检服务测试")
    print("=" * 60)
    
    # 设置测试数据库
    db = setup_test_db()
    
    try:
        # 创建测试数据
        conversation_id, user_id = create_test_data(db)
        print(f"✓ 创建测试对话: {conversation_id}")
        
        # 运行测试
        test_init_default_rules(db)
        test_inspect_message(db, conversation_id)
        test_inspect_conversation(db, conversation_id)
        test_generate_reports(db)
        test_rule_management(db)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)