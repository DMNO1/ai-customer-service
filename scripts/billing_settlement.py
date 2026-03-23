"""
计费结算脚本
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.order import Order, OrderStatus, Subscription
from app.core.feishu_service import feishu_service
import structlog

logger = structlog.get_logger()

def process_monthly_billing():
    """处理月度计费"""
    engine = create_engine(settings.database_url.replace("+psycopg2", "").replace("postgresql", "postgresql+psycopg2"))
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 查找即将过期的订阅（30天后）
        upcoming = session.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date <= datetime.utcnow() + timedelta(days=30)
        ).all()

        notifications = []
        for sub in upcoming:
            user = sub.order.user
            notifications.append({
                "user": user.email,
                "plan": sub.plan_id,
                "expires": sub.end_date.strftime("%Y-%m-%d")
            })

            # TODO: 发送邮件通知或自动续费
            logger.info("subscription_expiring", user_id=user.id, days_left=(sub.end_date - datetime.utcnow()).days)

        # 生成结算报告
        settled = session.query(Order).filter(
            Order.status == OrderStatus.PAID,
            Order.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count()

        feishu_text = f"""
📊 月度计费结算报告

今日新支付订单数: {settled}
待处理续订提醒: {len(notifications)}

续订提醒列表:
""" + "\n".join([f"- {n['user']} ({n['plan']}) 到期: {n['expires']}" for n in notifications[:10]])

        feishu_service.send_text(feishu_text.strip(), title="计费结算")
        logger.info("billing_settlement_completed", settled_orders=settled)

    except Exception as e:
        logger.error("billing_failed", error=str(e))
        raise
    finally:
        session.close()

if __name__ == "__main__":
    process_monthly_billing()
