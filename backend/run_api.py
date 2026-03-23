#!/usr/bin/env python
"""
API 服务启动脚本
"""

import os
import sys

# 添加项目路径到 PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.environment,
        reload_dirs=["./app"] if settings.debug else None
    )
