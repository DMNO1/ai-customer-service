"""
数据库初始化脚本
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

async def init_db():
    """初始化数据库"""
    # 使用同步引擎创建表（Alembic 负责迁移）
    from sqlalchemy import create_engine

    engine = create_engine(
        settings.database_url.replace("+psycopg2", "").replace("postgresql", "postgresql+psycopg2"),
        echo=settings.debug
    )

    try:
        # 创建所有表（仅用于开发/测试）
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表已创建")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
