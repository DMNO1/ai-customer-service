"""
订单与订阅模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models import Base, TimestampMixin)

class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    """支付方式"""
    ALIPAY = "alipay"
    WECHAT = "wechat"

class Order(Base, TimestampMixin):
    """订单表"""
    __tablename__ = "orders"

    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(50), nullable=False)  # basic/pro

    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    paid_at = Column(DateTime, nullable=True)

    # 支付回调数据
    payment_transaction_id = Column(String(100), nullable=True)
    payment_data = Column(String(4000), nullable=True)  # JSON 字符串

    # 关系
    user = relationship("User", back_populates="orders")
    subscription = relationship("Subscription", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"

class Subscription(Base, TimestampMixin):
    """订阅表"""
    __tablename__ = "subscriptions"

    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(50), nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)

    # 关系
    order = relationship("Order", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, end_date={self.end_date})>"
