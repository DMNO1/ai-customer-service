"""
知识库模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base, TimestampMixin

class KnowledgeBase(Base, TimestampMixin):
    """知识库表"""
    __tablename__ = "knowledge_bases"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # 关系
    owner = relationship("User", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name})>"

class Document(Base, TimestampMixin):
    """文档表"""
    __tablename__ = "documents"

    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, txt...
    file_size = Column(Integer, nullable=True)
    status = Column(String(20), default="processing")  # processing/completed/failed
    source_url = Column(String(2000), nullable=True)  # 如果来源是URL

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"
