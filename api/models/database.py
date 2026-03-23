"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    open_id = Column(String(100), unique=True, index=True)
    email = Column(String(200), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agents = relationship("Agent", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")

class Agent(Base):
    """Agent/Chatbot model"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    description = Column(Text, nullable=True)
    system_prompt = Column(Text)
    llm_provider = Column(String(50), default="openai")
    model_name = Column(String(100), default="gpt-3.5-turbo")
    knowledge_base_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = Column(JSON, default={})

    # Relationships
    owner = relationship("User", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent")

class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})

    # Relationships
    user = relationship("User", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """Individual message model"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeBaseDocument(Base):
    """Knowledge base document metadata"""
    __tablename__ = "knowledge_base_documents"

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(String(50), index=True)
    filename = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="processing")  # 'processing', 'ready', 'error'
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class PaymentOrder(Base):
    """Payment order model"""
    __tablename__ = "payment_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(100), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    plan_id = Column(String(50))
    amount = Column(Integer)  # in cents
    currency = Column(String(10), default="CNY")
    payment_method = Column(String(50))
    status = Column(String(50), default="pending")  # 'pending', 'paid', 'cancelled', 'refunded'
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class EmailLog(Base):
    """Email sending log"""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String(200))
    subject = Column(String(500))
    template_name = Column(String(100))
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="sent")  # 'sent', 'failed'
    error_message = Column(Text, nullable=True)
