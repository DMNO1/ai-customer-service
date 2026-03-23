"""
日志管理模块
提供统一的日志记录和飞书告警功能
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class FeishuAlertHandler(logging.Handler):
    """
    飞书告警日志处理器
    仅在错误级别及以上时发送飞书告警
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        super().__init__(level=logging.ERROR)
        self.webhook_url = webhook_url or os.getenv('FEISHU_ALERT_WEBHOOK')
        self.alert_cache = set()  # 防止重复告警
        
    def emit(self, record: logging.LogRecord):
        """发送飞书告警（仅在配置webhook时）"""
        if not self.webhook_url:
            return
            
        # 生成告警唯一标识（基于错误类型和消息前50字符）
        alert_key = f"{record.levelno}:{record.getMessage()[:50]}"
        
        # 防止5分钟内重复发送相同告警
        if alert_key in self.alert_cache:
            return
            
        try:
            import json
            import requests
            
            # 构建告警消息
            alert_message = {
                "msg_type": "interactive",
                "card": {
                    "config": {"wide_screen_mode": True},
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"🚨 AI客服系统告警 - {record.levelname}"
                        },
                        "template": "red" if record.levelno >= logging.ERROR else "orange"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**时间**: {datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')}\n**模块**: {record.module}\n**消息**: {record.getMessage()}"
                            }
                        }
                    ]
                }
            }
            
            # 异步发送（不阻塞主流程）
            requests.post(
                self.webhook_url,
                json=alert_message,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            self.alert_cache.add(alert_key)
            
        except Exception as e:
            # 告警发送失败时，记录到本地日志
            print(f"[ALERT_FAILED] Failed to send Feishu alert: {e}", file=sys.stderr)


def setup_logger(
    name: str,
    level: str = 'INFO',
    log_dir: Optional[str] = None,
    enable_feishu: bool = False
) -> logging.Logger:
    """
    配置并返回一个logger实例
    
    Args:
        name: logger名称
        level: 日志级别
        log_dir: 日志文件目录
        enable_feishu: 是否启用飞书告警
    
    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 主日志文件
        file_handler = logging.FileHandler(
            log_path / f'{name}_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # 错误日志文件（单独记录错误）
        error_handler = logging.FileHandler(
            log_path / f'{name}_error_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    # 飞书告警处理器
    if enable_feishu:
        feishu_handler = FeishuAlertHandler()
        logger.addHandler(feishu_handler)
    
    return logger


# 全局logger实例
system_logger = setup_logger(
    'ai_customer_service',
    level=os.getenv('LOG_LEVEL', 'INFO'),
    log_dir=os.getenv('LOG_DIR', 'logs'),
    enable_feishu=os.getenv('ENABLE_FEISHU_ALERT', 'false').lower() == 'true'
)
