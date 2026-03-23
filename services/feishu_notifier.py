"""
Feishu Notifier for AI Customer Service System
Handles sending notifications to Feishu chat groups
"""

import logging
import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import os


class FeishuNotifier:
    """
    Service class for sending notifications to Feishu
    """
    
    def __init__(self, webhook_url: Optional[str] = None, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        Initialize Feishu notifier
        
        Args:
            webhook_url: Feishu webhook URL (for incoming webhooks)
            app_id: Feishu app ID (for tenant access token)
            app_secret: Feishu app secret (for tenant access token)
        """
        self.webhook_url = webhook_url or os.getenv("FEISHU_WEBHOOK_URL")
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        # For chat messages using bot token
        self.bot_token = None
        self.bot_expire = 0
        
        logging.info("FeishuNotifier initialized")
    
    def _get_tenant_access_token(self) -> Optional[str]:
        """
        Get tenant access token from Feishu API
        
        Returns:
            Tenant access token or None if failed
        """
        if not self.app_id or not self.app_secret:
            logging.warning("FEISHU_APP_ID or FEISHU_APP_SECRET not set")
            return None
        
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                token = result.get("tenant_access_token")
                expire = result.get("expire", 3600)
                self.bot_expire = datetime.now().timestamp() + expire - 300  # Refresh 5 min before expiry
                self.bot_token = token
                logging.info("Successfully obtained Feishu tenant access token")
                return token
            else:
                logging.error(f"Failed to get Feishu token: {result.get('msg')}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting Feishu tenant access token: {str(e)}")
            return None
    
    def _ensure_token(self) -> Optional[str]:
        """
        Ensure we have a valid bot token, refresh if needed
        
        Returns:
            Valid bot token or None
        """
        if not self.bot_token or datetime.now().timestamp() >= self.bot_expire:
            return self._get_tenant_access_token()
        return self.bot_token
    
    def send_text_message(self, content: str, title: Optional[str] = None, chat_id: Optional[str] = None) -> Dict:
        """
        Send a text message to a Feishu chat
        
        Args:
            content: Message content (supports markdown)
            title: Optional message title
            chat_id: Chat ID to send to (uses FEISHU_DEFAULT_CHAT_ID if None)
            
        Returns:
            Result dictionary with success status
        """
        chat_id = chat_id or os.getenv("FEISHU_DEFAULT_CHAT_ID")
        if not chat_id:
            logging.error("No chat_id provided and FEISHU_DEFAULT_CHAT_ID not set")
            return {"success": False, "error": "No chat ID configured"}
        
        # Try webhook first if available
        if self.webhook_url:
            return self._send_via_webhook(content, title)
        
        # Otherwise use chat API
        token = self._ensure_token()
        if not token:
            return {"success": False, "error": "Failed to get bot token"}
        
        try:
            url = f"https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Build message content
            if title:
                message_content = {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": content
                            }
                        ]
                    ]
                }
            else:
                message_content = {
                    "text": content
                }
            
            params = {
                "receive_id_type": "chat_id",
                "receive_id": chat_id
            }
            
            data = {
                "content": json.dumps(message_content) if title else message_content,
                "msg_type": "interactive" if title else "text"
            }
            
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logging.info(f"Successfully sent Feishu message to chat {chat_id}")
                return {"success": True, "message_id": result.get("data", {}).get("message_id")}
            else:
                logging.error(f"Failed to send Feishu message: {result.get('msg')}")
                return {"success": False, "error": result.get("msg")}
                
        except Exception as e:
            logging.error(f"Error sending Feishu message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _send_via_webhook(self, content: str, title: Optional[str] = None) -> Dict:
        """
        Send message via incoming webhook
        
        Args:
            content: Message content
            title: Optional title
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Build webhook payload
            if title:
                payload = {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": content
                            }
                        ]
                    ]
                }
            else:
                payload = {
                    "text": content
                }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info("Successfully sent Feishu message via webhook")
            return {"success": True}
            
        except Exception as e:
            logging.error(f"Error sending Feishu message via webhook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_system_alert(self, alert_type: str, message: str, details: Optional[Dict] = None, chat_id: Optional[str] = None):
        """
        Send a system alert notification
        
        Args:
            alert_type: Type of alert (error, warning, info, success)
            message: Alert message
            details: Optional additional details
            chat_id: Chat ID to send to
        """
        # Define emoji based on alert type
        emoji_map = {
            "error": "🔴",
            "warning": "🟡",
            "info": "🔵",
            "success": "🟢"
        }
        emoji = emoji_map.get(alert_type, "📢")
        
        # Build message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{emoji} **{alert_type.upper()}**\n"
        full_message += f"**Time**: {timestamp}\n"
        full_message += f"**Message**: {message}\n"
        
        if details:
            full_message += "\n**Details**:\n"
            for key, value in details.items():
                full_message += f"- {key}: {value}\n"
        
        # Send as title with content
        title = f"System Alert: {alert_type}"
        return self.send_text_message(full_message, title=title, chat_id=chat_id)
    
    def send_daily_report(self, report_data: Dict, chat_id: Optional[str] = None):
        """
        Send daily operational report
        
        Args:
            report_data: Dictionary containing report metrics
            chat_id: Chat ID to send to
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        message = f"📊 **Daily Report - {timestamp}**\n\n"
        
        # Expected keys in report_data
        sections = [
            ("Overview", ["total_users", "active_users", "new_users"]),
            ("Conversations", ["total_conversations", "avg_response_time", "satisfaction_rate"]),
            ("Knowledge Base", ["total_documents", "vector_count", "search_count"]),
            ("System", ["api_requests", "errors", "uptime"])
        ]
        
        for section_name, keys in sections:
            message += f"**{section_name}:**\n"
            for key in keys:
                if key in report_data:
                    value = report_data[key]
                    if isinstance(value, float):
                        value = f"{value:.2f}"
                    message += f"- {key.replace('_', ' ').title()}: {value}\n"
            message += "\n"
        
        title = f"Daily Operations Report - {timestamp}"
        return self.send_text_message(message, title=title, chat_id=chat_id)
    
    def send_user_activity_alert(self, user_id: str, action: str, details: Optional[Dict] = None, chat_id: Optional[str] = None):
        """
        Send alert for important user activities
        
        Args:
            user_id: User ID
            action: Action performed (registration, subscription, etc.)
            details: Additional details
            chat_id: Chat ID to send to
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"👤 **User Activity**\n"
        message += f"**Time**: {timestamp}\n"
        message += f"**User ID**: {user_id}\n"
        message += f"**Action**: {action}\n"
        
        if details:
            message += "\n**Details**:\n"
            for key, value in details.items():
                message += f"- {key}: {value}\n"
        
        title = f"User Activity: {action}"
        return self.send_text_message(message, title=title, chat_id=chat_id)


# Initialize logging
logging.basicConfig(level=logging.INFO)


def test_feishu_notifier():
    """
    Test function for Feishu notifier
    """
    print("Testing Feishu Notifier...")
    
    notifier = FeishuNotifier()
    print("Available configuration:")
    print(f"  Webhook URL: {'Set' if notifier.webhook_url else 'Not set'}")
    print(f"  App ID: {'Set' if notifier.app_id else 'Not set'}")
    print(f"  Default Chat ID: {os.getenv('FEISHU_DEFAULT_CHAT_ID', 'Not set')}")
    
    # Note: Actual sending requires proper configuration
    print("FeishuNotifier initialized (requires configuration to send messages)")


if __name__ == "__main__":
    test_feishu_notifier()