"""
Email Notifier
发送系统邮件和通知。
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    def send_email(self, to: List[str], subject: str, body: str, is_html: bool = False) -> bool:
        """
        发送电子邮件。
        
        Args:
            to: 收件人邮箱列表。
            subject: 邮件主题。
            body: 邮件正文。
            is_html: 是否为HTML格式。
            
        Returns:
            如果发送成功则返回True，否则返回False。
        """
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            print("SMTP configuration is incomplete")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ", ".join(to)
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, to, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_system_notification(self, to: List[str], event_type: str, details: str) -> bool:
        """
        发送系统通知邮件。
        
        Args:
            to: 收件人邮箱列表。
            event_type: 事件类型（如"error", "warning", "info"）。
            details: 事件详情。
            
        Returns:
            如果发送成功则返回True，否则返回False。
        """
        subject = f"[AI客服系统] {event_type.upper()} Notification"
        body = f"""
        系统事件: {event_type}
        详情: {details}
        时间: {self._get_current_time()}
        
        此邮件由AI智能客服系统自动发送。
        """
        return self.send_email(to, subject, body)
    
    def _get_current_time(self) -> str:
        """获取当前时间的字符串表示"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 用于测试的主函数
if __name__ == "__main__":
    notifier = EmailNotifier()
    
    # 测试发送邮件（需要配置SMTP）
    # success = notifier.send_email(
    #     ["test@example.com"],
    #     "Test Email",
    #     "This is a test email from the AI Customer Service system."
    # )
    # print(f"Email sent: {success}")
    # 
    # # 测试发送系统通知
    # success = notifier.send_system_notification(
    #     ["admin@example.com"],
    #     "info",
    #     "System started successfully."
    # )
    # print(f"Notification sent: {success}")