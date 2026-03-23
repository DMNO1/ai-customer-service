"""
对话质检模块 (Quality Assurance Module)

提供AI客服对话的自动质量检测功能，包括：
- 响应时间分析
- 满意度评估
- 敏感词检测
- 对话完整性检查
- 综合质量评分
"""

from .quality_service import QualityService
from .quality_report import QualityReport, ConversationMetrics
from .analyzer import ConversationAnalyzer

__all__ = [
    'QualityService',
    'QualityReport', 
    'ConversationMetrics',
    'ConversationAnalyzer'
]
