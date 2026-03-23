"""
Database Models for AI Customer Service System
SQLAlchemy models aligned with Alembic migrations
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

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
    vector_collection_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
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
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    provider_used: Mapped[Optional[str]] = mapped_column(String(50))
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default='active')
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="conversations")
    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


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
    search_results: Mapped[Optional[dict]] = mapped_column(JSONB)
    sources: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class Subscription(Base):
    """
    User subscription and billing information
    """
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index('ix_subscriptions_user_id', 'user_id'),
        Index('ix_subscriptions_status', 'status'),
        Index('ix_subscriptions_plan_id', 'plan_id'),
    )
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='active')
    billing_cycle: Mapped[str] = mapped_column(String(20), default='monthly')
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    limits: Mapped[dict] = mapped_column(JSONB, default={})  # { "messages_per_month": 1000, "knowledge_bases": 3 }
    usage: Mapped[dict] = mapped_column(JSONB, default={})  # { "messages_used": 450, "knowledge_bases_used": 2 }
    payment_provider: Mapped[Optional[str]] = mapped_column(String(50))
    payment_id: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")


class AuditLog(Base):
    """
    Audit log for tracking important system events
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
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    details: Mapped[dict] = mapped_column(JSONB, default={})
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)