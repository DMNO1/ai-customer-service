"""
Database Models for AI Customer Service System
SQLAlchemy models aligned with Alembic migrations
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, 
    ForeignKey, Index, JSON as SQLJSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column

Base = declarative_base()


class User(Base):
    """
    User model for authentication and profile
    """
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_username', 'username'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    company_name: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    timezone: Mapped[str] = mapped_column(String(50), default='Asia/Shanghai')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default='user')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="user")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user")
    quality_inspections: Mapped[List["QualityInspection"]] = relationship("QualityInspection", back_populates="inspector")


class KnowledgeBase(Base):
    """
    Knowledge base metadata and configuration
    """
    __tablename__ = "knowledge_bases"
    __table_args__ = (
        Index('ix_knowledge_bases_user_id', 'user_id'),
        Index('ix_knowledge_bases_vector_collection', 'vector_collection_name'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    settings: Mapped[dict] = mapped_column(JSONB, default={})
    vector_collection_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # ChromaDB collection name
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="knowledge_bases")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="knowledge_base")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="knowledge_base")


class Document(Base):
    """
    Document tracking and processing status
    """
    __tablename__ = "documents"
    __table_args__ = (
        Index('ix_documents_kb_id', 'knowledge_base_id'),
        Index('ix_documents_status', 'status'),
        Index('ix_documents_file_hash', 'file_hash'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    knowledge_base_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('knowledge_bases.id'), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64))
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    content_length: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    doc_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    status: Mapped[str] = mapped_column(String(50), default='pending')
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", back_populates="documents")


class Conversation(Base):
    """
    Conversation session tracking
    """
    __tablename__ = "conversations"
    __table_args__ = (
        Index('ix_conversations_user_id', 'user_id'),
        Index('ix_conversations_kb_id', 'knowledge_base_id'),
        Index('ix_conversations_session_id', 'session_id'),
        Index('ix_conversations_created_at', 'created_at'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    knowledge_base_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('knowledge_bases.id'), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)  # Client-side session identifier
    title: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    provider_used: Mapped[Optional[str]] = mapped_column(String(50))  # Which LLM provider was used
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 rating
    status: Mapped[str] = mapped_column(String(50), default='active')  # active, ended, archived
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="conversations")
    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    quality_inspections: Mapped[List["QualityInspection"]] = relationship("QualityInspection", back_populates="conversation")


class Message(Base):
    """
    Individual message within a conversation
    """
    __tablename__ = "messages"
    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_created_at', 'created_at'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    search_results: Mapped[dict] = mapped_column(JSONB)  # RAG search results used
    sources: Mapped[dict] = mapped_column(JSONB)  # Source documents referenced
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    quality_inspections: Mapped[List["QualityInspection"]] = relationship("QualityInspection", back_populates="message")


class Subscription(Base):
    """
    User subscription and billing
    """
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index('ix_subscriptions_user_id', 'user_id'),
        Index('ix_subscriptions_status', 'status'),
        Index('ix_subscriptions_plan_id', 'plan_id'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False)  # free, basic, pro, enterprise
    status: Mapped[str] = mapped_column(String(50), default='active')  # active, canceled, expired
    billing_cycle: Mapped[str] = mapped_column(String(20), default='monthly')  # monthly, yearly
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    limits: Mapped[dict] = mapped_column(JSONB, default={})  # Usage limits per period
    usage: Mapped[dict] = mapped_column(JSONB, default={})  # Current usage stats
    payment_provider: Mapped[Optional[str]] = mapped_column(String(50))  # alipay, wechat, stripe
    payment_id: Mapped[Optional[str]] = mapped_column(String(200))  # External payment reference
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="subscription")


class Order(Base):
    """
    Order and payment tracking
    """
    __tablename__ = "orders"
    __table_args__ = (
        Index('ix_orders_order_number', 'order_number'),
        Index('ix_orders_user_id', 'user_id'),
        Index('ix_orders_status', 'status'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(sa.Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='pending')  # pending, paid, cancelled, refunded
    payment_method: Mapped[str] = mapped_column(String(50))  # alipay, wechat, stripe
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    # Payment callback data
    payment_transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    payment_data: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="order", uselist=False)


class QualityInspection(Base):
    """对话质检记录表"""
    __tablename__ = "quality_inspections"
    __table_args__ = (
        Index('ix_quality_inspections_conversation_id', 'conversation_id'),
        Index('ix_quality_inspections_message_id', 'message_id'),
        Index('ix_quality_inspections_created_at', 'created_at'),
        Index('ix_quality_inspections_score', 'quality_score'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    message_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('messages.id'), nullable=True)
    inspection_type: Mapped[str] = mapped_column(String(50), default='auto')  # auto, manual
    response_time_seconds: Mapped[float] = mapped_column(sa.Float, default=0.0)
    keywords_detected: Mapped[str] = mapped_column(Text, default='[]')  # JSON array
    quality_score: Mapped[int] = mapped_column(Integer, default=0)
    has_issues: Mapped[bool] = mapped_column(Boolean, default=False)
    issues_found: Mapped[str] = mapped_column(Text, default='[]')  # JSON array
    inspector_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="quality_inspections")
    message: Mapped[Optional["Message"]] = relationship("Message", back_populates="quality_inspections")
    inspector: Mapped[Optional["User"]] = relationship("User", back_populates="quality_inspections")


class QualityRule(Base):
    """质检规则配置表"""
    __tablename__ = "quality_rules"
    __table_args__ = (
        Index('ix_quality_rules_type', 'rule_type'),
        Index('ix_quality_rules_active', 'is_active'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    score_impact: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """
    Audit log for tracking important events
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('ix_audit_logs_user_id', 'user_id'),
        Index('ix_audit_logs_action', 'action'),
        Index('ix_audit_logs_created_at', 'created_at'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))  # knowledge_base, document, conversation, etc.
    resource_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    details: Mapped[dict] = mapped_column(JSONB, default={})
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Add relationship to existing models that were defined earlier
User.orders = relationship("Order", back_populates="user")
User.subscriptions = relationship("Subscription", back_populates="user")
Order.user = relationship("User", back_populates="orders")
Order.subscription = relationship("Subscription", back_populates="order")
Subscription.order = relationship("Order", back_populates="subscription")