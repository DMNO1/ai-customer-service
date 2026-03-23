"""
用户模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base, TimestampMixin

class User(Base, TimestampMixin):
    """用户表"""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # 关系
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner")
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
