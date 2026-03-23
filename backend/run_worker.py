#!/usr/bin/env python
"""
Celery Worker 启动脚本
"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from celery import Celery
from app.core.config import settings

app = Celery(
    'ai_customer_service',
    broker=settings.redis_url,
    backend=settings.redis_url
)

# 配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=29 * 60,
)

# 自动发现任务
app.autodiscover_tasks(['app.tasks'])

if __name__ == "__main__":
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--hostname=worker@%h'
    ]
    app.worker_main(argv)
