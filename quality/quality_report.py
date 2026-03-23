"""
质检报告模型 (Quality Report Models)

定义对话质检报告的数据结构和模型。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class QualityStatus(Enum):
    """质检状态枚举"""
    PASS = "pass"           # 通过
    FAIL = "fail"           # 不通过
    WARNING = "warning"     # 警告
    PENDING = "pending"     # 待检查


@dataclass
class ConversationMetrics:
    """对话指标数据类"""
    
    # 响应时间指标
    avg_response_time: float = 0.0          # 平均响应时间(秒)
    max_response_time: float = 0.0          # 最大响应时间(秒)
    timeout_count: int = 0                  # 超时次数
    
    # 对话内容指标
    message_count: int = 0                  # 消息总数
    user_message_count: int = 0             # 用户消息数
    ai_message_count: int = 0               # AI消息数
    
    # 质量指标
    sensitive_words: List[str] = field(default_factory=list)  # 检测到的敏感词
    sensitive_word_count: int = 0           # 敏感词出现次数
    
    # 完整性指标
    is_complete: bool = True                # 对话是否正常结束
    has_greeting: bool = False              # 是否有问候语
    has_farewell: bool = False              # 是否有结束语
    
    # 用户反馈
    user_rating: Optional[int] = None       # 用户评分(1-5)
    user_feedback: Optional[str] = None     # 用户反馈文本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "avg_response_time": self.avg_response_time,
            "max_response_time": self.max_response_time,
            "timeout_count": self.timeout_count,
            "message_count": self.message_count,
            "user_message_count": self.user_message_count,
            "ai_message_count": self.ai_message_count,
            "sensitive_words": self.sensitive_words,
            "sensitive_word_count": self.sensitive_word_count,
            "is_complete": self.is_complete,
            "has_greeting": self.has_greeting,
            "has_farewell": self.has_farewell,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback
        }


@dataclass
class QualityReport:
    """质检报告数据类"""
    
    # 基本信息
    report_id: str                          # 报告ID
    conversation_id: str                    # 对话ID
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    checked_at: Optional[datetime] = None   # 检查时间
    
    # 质检结果
    status: QualityStatus = QualityStatus.PENDING  # 质检状态
    score: float = 0.0                      # 综合评分(0-100)
    
    # 详细指标
    metrics: ConversationMetrics = field(default_factory=ConversationMetrics)
    
    # 问题列表
    issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # 建议
    suggestions: List[str] = field(default_factory=list)
    
    # 备注
    notes: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.checked_at is None:
            self.checked_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
            "status": self.status.value,
            "score": self.score,
            "metrics": self.metrics.to_dict(),
            "issues": self.issues,
            "suggestions": self.suggestions,
            "notes": self.notes
        }
    
    def add_issue(self, category: str, severity: str, description: str, 
                  details: Optional[Dict] = None):
        """添加问题"""
        self.issues.append({
            "category": category,
            "severity": severity,
            "description": description,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def add_suggestion(self, suggestion: str):
        """添加建议"""
        self.suggestions.append(suggestion)
    
    def set_status_from_score(self):
        """根据分数设置状态"""
        if self.score >= 80:
            self.status = QualityStatus.PASS
        elif self.score >= 60:
            self.status = QualityStatus.WARNING
        else:
            self.status = QualityStatus.FAIL


class QualityReportCollection:
    """质检报告集合"""
    
    def __init__(self):
        self.reports: List[QualityReport] = []
    
    def add_report(self, report: QualityReport):
        """添加报告"""
        self.reports.append(report)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取汇总统计"""
        if not self.reports:
            return {
                "total": 0,
                "pass_count": 0,
                "fail_count": 0,
                "warning_count": 0,
                "avg_score": 0.0
            }
        
        total = len(self.reports)
        pass_count = sum(1 for r in self.reports if r.status == QualityStatus.PASS)
        fail_count = sum(1 for r in self.reports if r.status == QualityStatus.FAIL)
        warning_count = sum(1 for r in self.reports if r.status == QualityStatus.WARNING)
        avg_score = sum(r.score for r in self.reports) / total
        
        return {
            "total": total,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "warning_count": warning_count,
            "avg_score": round(avg_score, 2),
            "pass_rate": round(pass_count / total * 100, 2)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary": self.get_summary(),
            "reports": [r.to_dict() for r in self.reports]
        }
