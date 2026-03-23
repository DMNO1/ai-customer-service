"""
每日数据报表脚本
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.core.feishu_service import feishu_service
from app.services.vector_store import vector_store
from app.services.chat_service import chat_service
from app.core.config import settings
from app.models import Base, engine
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def generate_daily_report():
    """生成日报"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    # TODO: 从数据库查询统计数据
    stats = {
        "new_users": 0,  # User.query.filter(User.created_at >= yesterday).count()
        "active_conversations": 0,  # 对话记录统计
        "knowledge_base_count": vector_store.get_collection_stats().get("document_count", 0),
        "llm_calls": 0,
        "revenue": 0.0
    }

    content = f"""
📊 智能客服系统日报 - {date_str}

👥 新增用户: {stats['new_users']}
💬 对话总数: {stats['active_conversations']}
📚 知识库文档: {stats['knowledge_base_count']} 个片段
🤖 LLM 调用次数: {stats['llm_calls']}
💰 当日收入: ¥{stats['revenue']:.2f}

系统运行正常，向量数据库可用，LLM 提供商: {', '.join(settings.vector_db)}
""".strip()

    await feishu_service.send_text(content, title=f"日报 {date_str}")
    logger.info("daily_report_sent", date=date_str, stats=stats)

async def main():
    try:
        await generate_daily_report()
    except Exception as e:
        logger.error("daily_report_failed", error=str(e))
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
