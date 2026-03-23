"""
飞书通知服务
支持机器人群消息推送
"""

import httpx
import json
from typing import Optional, Dict, Any, List
from app.core.exceptions import FeishuNotificationException
from app.core.config import settings
import structlog

logger = structlog.get_logger()

class FeishuService:
    """飞书消息推送服务"""

    def __init__(self):
        self.webhook_url = settings.feishu_webhook_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def send_text(
        self,
        content: str,
        title: Optional[str] = None,
        at_all: bool = False,
        at_user_ids: Optional[List[str]] = None
    ) -> bool:
        """
        发送文本消息到飞书群

        Args:
            content: 消息内容
            title: 消息标题（可选）
            at_all: 是否 @ 全员
            at_user_ids: 要 @ 的用户ID列表

        Returns:
            bool: 发送是否成功
        """
        if not self.webhook_url:
            logger.warning("feishu_webhook_url not configured, skipping notification")
            return False

        payload = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n\n{content}" if title else content
            }
        }

        # 添加 @ 功能
        if at_all or at_user_ids:
            payload["content"]["text"] += "\n"
            if at_all:
                payload["content"]["text"] += "<at user_id=\"all\">所有人</at> "
            if at_user_ids:
                for uid in at_user_ids:
                    payload["content"]["text"] += f"<at user_id=\"{uid}\"> </at> "

        try:
            resp = await self.http_client.post(self.webhook_url, json=payload)
            resp.raise_for_status()
            result = resp.json()

            if result.get("StatusCode") == 0:
                logger.info("feishu_message_sent", title=title)
                return True
            else:
                raise FeishuNotificationException(
                    f"飞书消息发送失败: {result.get('StatusMessage')}",
                    self.webhook_url
                )

        except httpx.RequestError as e:
            logger.error("feishu_request_failed", error=str(e))
            raise FeishuNotificationException(f"请求飞书失败: {str(e)}", self.webhook_url)
        except Exception as e:
            logger.error("feishu_send_error", error=str(e))
            return False

    async def send_card(
        self,
        title: str,
        content: str,
        theme_color: str = "blue",
        fields: Optional[List[Dict[str, str]]] = None,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None
    ) -> bool:
        """
        发送卡片消息

        Args:
            title: 卡片标题
            content: 卡片内容
            theme_color: 主题颜色（blue/green/orange/red）
            fields: 字段列表 [{"title": "字段名", "value": "值"}]
            button_text: 按钮文字
            button_url: 按钮链接

        Returns:
            bool: 发送是否成功
        """
        if not self.webhook_url:
            return False

        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": theme_color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": content
                    }
                }
            ]
        }

        if fields:
            field_elements = []
            for f in fields:
                field_elements.append({
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": False,
                            "text": {
                                "tag": "plain_text",
                                "content": f["title"]
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "plain_text",
                                "content": f["value"]
                            }
                        }
                    ]
                })
            card["elements"].extend(field_elements)

        if button_text and button_url:
            card["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button_text
                        },
                        "type": "default",
                        "url": button_url
                    }
                ]
            })

        payload = {
            "msg_type": "interactive",
            "card": card
        }

        try:
            resp = await self.http_client.post(self.webhook_url, json=payload)
            resp.raise_for_status()
            result = resp.json()

            if result.get("StatusCode") == 0:
                logger.info("feishu_card_sent", title=title)
                return True
            else:
                raise FeishuNotificationException(
                    f"飞书卡片发送失败: {result.get('StatusMessage')}",
                    self.webhook_url
                )

        except Exception as e:
            logger.error("feishu_card_send_error", error=str(e))
            return False

    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


# 全局飞书服务实例
feishu_service = FeishuService()
