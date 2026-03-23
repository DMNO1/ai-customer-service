"""
数据清理脚本
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import structlog
import shutil

logger = structlog.get_logger()

def cleanup_temp_files():
    """清理临时文件"""
    tmp_dir = os.path.join(project_root, "tmp")
    if os.path.exists(tmp_dir):
        try:
            shutil.rmtree(tmp_dir)
            os.makedirs(tmp_dir, exist_ok=True)
            logger.info("temp_files_cleaned", path=tmp_dir)
        except Exception as e:
            logger.warning("temp_cleanup_failed", error=str(e))

def archive_old_logs():
    """归档旧日志"""
    logs_dir = os.path.join(project_root, "logs")
    if not os.path.exists(logs_dir):
        return

    cutoff = datetime.utcnow() - timedelta(days=30)
    for filename in os.listdir(logs_dir):
        filepath = os.path.join(logs_dir, filename)
        try:
            mtime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                # 压缩并移动到 archive 子目录
                archive_dir = os.path.join(logs_dir, "archive")
                os.makedirs(archive_dir, exist_ok=True)
                shutil.move(filepath, os.path.join(archive_dir, filename))
                logger.info("log_archived", file=filename)
        except Exception as e:
            logger.warning("log_archive_failed", file=filename, error=str(e))

def cleanup_old_conversations():
    """清理7天前的对话历史（内存存储）"""
    # 注意：这只是清理内存中的会话，实际数据库清理需要另外实现
    from app.api.chat import _conversations
    initial_count = len(_conversations)
    # 简单清理策略：数量限制为最近 1000 个
    if len(_conversations) > 1000:
        keys_to_remove = list(_conversations.keys())[:-1000]
        for k in keys_to_remove:
            del _conversations[k]
        logger.info("conversations_cleaned", removed=len(keys_to_remove), remaining=len(_conversations))

def main():
    """清理任务主函数"""
    logger.info("data_cleanup_started")

    cleanup_temp_files()
    archive_old_logs()
    cleanup_old_conversations()

    logger.info("data_cleanup_completed")

if __name__ == "__main__":
    main()
