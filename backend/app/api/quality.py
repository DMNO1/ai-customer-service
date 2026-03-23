"""
对话质检API模块
提供质检规则管理、质检执行、报告查询等功能
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, QualityRule, QualityInspection
from app.services.quality_service import (
    QualityInspectionEngine,
    QualityReportService,
    QualityRuleService,
    init_quality_rules
)

router = APIRouter(prefix="/quality", tags=["quality"])


# ============ Pydantic Models ============

class QualityRuleCreate(BaseModel):
    rule_name: str = Field(..., min_length=1, max_length=100)
    rule_type: str = Field(..., regex="^(response_time|keywords|length|sentiment|sensitive_words|format)$")
    condition: dict
    score_impact: int = Field(default=0)
    is_active: bool = Field(default=True)


class QualityRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_type: Optional[str] = Field(None, regex="^(response_time|keywords|length|sentiment|sensitive_words|format)$")
    condition: Optional[dict] = None
    score_impact: Optional[int] = None
    is_active: Optional[bool] = None


class QualityRuleResponse(BaseModel):
    id: int
    rule_name: str
    rule_type: str
    condition: dict
    score_impact: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InspectionRequest(BaseModel):
    conversation_id: UUID


class InspectionResponse(BaseModel):
    id: int
    conversation_id: UUID
    message_id: Optional[UUID]
    inspection_type: str
    response_time_seconds: float
    keywords_detected: List[str]
    quality_score: int
    has_issues: bool
    issues_found: List[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DailyReportResponse(BaseModel):
    date: str
    total_inspected: int
    average_score: float
    issues_count: int
    issues_rate: float
    average_response_time: float
    issue_breakdown: dict
    low_score_conversations: List[dict]
    generated_at: str


class ConversationReportResponse(BaseModel):
    conversation_id: str
    total_messages: int
    average_score: float
    messages: List[dict]


class TrendsResponse(BaseModel):
    trends: List[dict]


# ============ API Endpoints ============

@router.post("/rules/init", response_model=dict)
def initialize_default_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """初始化默认质检规则（管理员权限）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    count = init_quality_rules(db)
    return {"message": f"成功初始化 {count} 条默认规则", "created_count": count}


@router.get("/rules", response_model=List[QualityRuleResponse])
def list_rules(
    active_only: bool = Query(False, description="仅显示启用规则"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取质检规则列表"""
    service = QualityRuleService(db)
    rules = service.get_rules(active_only=active_only)
    
    # 解析condition JSON
    result = []
    for rule in rules:
        rule_dict = {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "condition": __import__('json').loads(rule.condition),
            "score_impact": rule.score_impact,
            "is_active": rule.is_active,
            "created_at": rule.created_at,
            "updated_at": rule.updated_at
        }
        result.append(rule_dict)
    
    return result


@router.get("/rules/{rule_id}", response_model=QualityRuleResponse)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个规则详情"""
    service = QualityRuleService(db)
    rule = service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "id": rule.id,
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "condition": __import__('json').loads(rule.condition),
        "score_impact": rule.score_impact,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }


@router.post("/rules", response_model=QualityRuleResponse)
def create_rule(
    rule_data: QualityRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新质检规则（管理员权限）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = QualityRuleService(db)
    rule = service.create_rule(rule_data.dict())
    
    return {
        "id": rule.id,
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "condition": __import__('json').loads(rule.condition),
        "score_impact": rule.score_impact,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }


@router.put("/rules/{rule_id}", response_model=QualityRuleResponse)
def update_rule(
    rule_id: int,
    rule_data: QualityRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新质检规则（管理员权限）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = QualityRuleService(db)
    rule = service.update_rule(rule_id, rule_data.dict(exclude_unset=True))
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "id": rule.id,
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "condition": __import__('json').loads(rule.condition),
        "score_impact": rule.score_impact,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除质检规则（管理员权限）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = QualityRuleService(db)
    success = service.delete_rule(rule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {"message": "规则已删除"}


# ============ Inspection Endpoints ============

@router.post("/inspect", response_model=List[InspectionResponse])
def inspect_conversation(
    request: InspectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """对指定对话进行质检"""
    engine = QualityInspectionEngine(db)
    inspections = engine.inspect_conversation(request.conversation_id)
    
    result = []
    for inspection in inspections:
        result.append({
            "id": inspection.id,
            "conversation_id": inspection.conversation_id,
            "message_id": inspection.message_id,
            "inspection_type": inspection.inspection_type,
            "response_time_seconds": inspection.response_time_seconds,
            "keywords_detected": __import__('json').loads(inspection.keywords_detected),
            "quality_score": inspection.quality_score,
            "has_issues": inspection.has_issues,
            "issues_found": __import__('json').loads(inspection.issues_found),
            "created_at": inspection.created_at
        })
    
    return result


@router.get("/inspections", response_model=List[InspectionResponse])
def list_inspections(
    conversation_id: Optional[UUID] = Query(None),
    has_issues: Optional[bool] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询质检记录"""
    query = db.query(QualityInspection)
    
    if conversation_id:
        query = query.filter(QualityInspection.conversation_id == conversation_id)
    if has_issues is not None:
        query = query.filter(QualityInspection.has_issues == has_issues)
    if min_score is not None:
        query = query.filter(QualityInspection.quality_score >= min_score)
    if max_score is not None:
        query = query.filter(QualityInspection.quality_score <= max_score)
    
    inspections = query.order_by(QualityInspection.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for inspection in inspections:
        result.append({
            "id": inspection.id,
            "conversation_id": inspection.conversation_id,
            "message_id": inspection.message_id,
            "inspection_type": inspection.inspection_type,
            "response_time_seconds": inspection.response_time_seconds,
            "keywords_detected": __import__('json').loads(inspection.keywords_detected),
            "quality_score": inspection.quality_score,
            "has_issues": inspection.has_issues,
            "issues_found": __import__('json').loads(inspection.issues_found),
            "created_at": inspection.created_at
        })
    
    return result


# ============ Report Endpoints ============

@router.get("/reports/daily", response_model=DailyReportResponse)
def get_daily_report(
    date: Optional[str] = Query(None, description="报告日期 (YYYY-MM-DD)，默认为昨天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取每日质检报告"""
    report_date = None
    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    service = QualityReportService(db)
    report = service.generate_daily_report(report_date)
    
    return report


@router.get("/reports/conversation/{conversation_id}", response_model=ConversationReportResponse)
def get_conversation_report(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个对话的质检报告"""
    service = QualityReportService(db)
    report = service.generate_conversation_report(conversation_id)
    
    if "message" in report:
        raise HTTPException(status_code=404, detail=report["message"])
    
    return report


@router.get("/reports/trends", response_model=TrendsResponse)
def get_quality_trends(
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取质检趋势"""
    service = QualityReportService(db)
    trends = service.get_quality_trends(days)
    
    return {"trends": trends}


# ============ Background Tasks ============

@router.post("/inspect/batch")
def batch_inspect(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量质检（异步任务，管理员权限）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    def run_batch_inspection():
        """后台执行批量质检"""
        from app.models.models import Conversation
        
        # 获取最近7天未质检的对话
        week_ago = datetime.utcnow() - timedelta(days=7)
        conversations = db.query(Conversation).filter(
            Conversation.created_at >= week_ago,
            Conversation.status == 'ended'
        ).all()
        
        engine = QualityInspectionEngine(db)
        total_inspected = 0
        
        for conversation in conversations:
            # 检查是否已有质检记录
            existing = db.query(QualityInspection).filter(
                QualityInspection.conversation_id == conversation.id
            ).first()
            
            if not existing:
                engine.inspect_conversation(conversation.id)
                total_inspected += 1
        
        __import__('logging').getLogger(__name__).info(f"Batch inspection completed: {total_inspected} conversations")
    
    background_tasks.add_task(run_batch_inspection)
    
    return {"message": "批量质检任务已启动", "status": "running"}


@router.get("/stats/overview")
def get_quality_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取质检概览统计"""
    from sqlalchemy import func
    
    # 总质检数
    total_count = db.query(func.count(QualityInspection.id)).scalar()
    
    # 问题数
    issues_count = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.has_issues == True
    ).scalar()
    
    # 平均分
    avg_score = db.query(func.avg(QualityInspection.quality_score)).scalar()
    
    # 今日质检数
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(func.count(QualityInspection.id)).filter(
        QualityInspection.created_at >= today
    ).scalar()
    
    return {
        "total_inspections": total_count,
        "issues_count": issues_count,
        "issues_rate": round((issues_count / total_count * 100) if total_count > 0 else 0, 2),
        "average_score": round(float(avg_score or 0), 2),
        "today_inspections": today_count
    }