"""
Initial schema migration for AI Customer Service System

Creates core tables:
- users (user management)
- knowledge_bases (knowledge base metadata)
- documents (document tracking)
- conversations (chat conversation logs)
- messages (individual messages in conversations)
- subscriptions (billing and subscriptions)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


def upgrade():
    """Create initial database schema"""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200)),
        sa.Column('company_name', sa.String(200)),
        sa.Column('phone', sa.String(50)),
        sa.Column('timezone', sa.String(50), default='Asia/Shanghai'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('role', sa.String(50), default='user'),  # user, admin, super_admin
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('last_login_at', sa.DateTime)
    )
    
    # Create indexes for users
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create knowledge_bases table
    op.create_table(
        'knowledge_bases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('settings', postgresql.JSONB, default={}),  # Configuration settings
        sa.Column('vector_collection_name', sa.String(100), unique=True, nullable=False),  # ChromaDB collection name
        sa.Column('document_count', sa.Integer, default=0),
        sa.Column('total_chunks', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Create indexes for knowledge_bases
    op.create_index('ix_knowledge_bases_user_id', 'knowledge_bases', ['user_id'])
    op.create_index('ix_knowledge_bases_vector_collection', 'knowledge_bases', ['vector_collection_name'])
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('knowledge_base_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('knowledge_bases.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer),  # Size in bytes
        sa.Column('file_hash', sa.String(64)),  # SHA256 hash for deduplication
        sa.Column('mime_type', sa.String(100)),
        sa.Column('content_length', sa.Integer),  # Extracted text length
        sa.Column('chunk_count', sa.Integer, default=0),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('status', sa.String(50), default='pending'),  # pending, processing, completed, failed
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('processed_at', sa.DateTime)
    )
    
    # Create indexes for documents
    op.create_index('ix_documents_kb_id', 'documents', ['knowledge_base_id'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'])
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('knowledge_base_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('knowledge_bases.id'), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=False),  # Client-side session identifier
        sa.Column('title', sa.String(200)),
        sa.Column('summary', sa.Text),
        sa.Column('message_count', sa.Integer, default=0),
        sa.Column('tokens_used', sa.Integer, default=0),
        sa.Column('provider_used', sa.String(50)),  # Which LLM provider was used
        sa.Column('satisfaction_rating', sa.Integer),  # 1-5 rating
        sa.Column('status', sa.String(50), default='active'),  # active, ended, archived
        sa.Column('ended_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Create indexes for conversations
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_kb_id', 'conversations', ['knowledge_base_id'])
    op.create_index('ix_conversations_session_id', 'conversations', ['session_id'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),  # user, assistant, system
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tokens', sa.Integer, default=0),
        sa.Column('search_results', postgresql.JSONB),  # RAG search results used
        sa.Column('sources', postgresql.JSONB),  # Source documents referenced
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Create indexes for messages
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan_id', sa.String(50), nullable=False),  # free, basic, pro, enterprise
        sa.Column('status', sa.String(50), default='active'),  # active, canceled, expired
        sa.Column('billing_cycle', sa.String(20), default='monthly'),  # monthly, yearly
        sa.Column('current_period_start', sa.DateTime),
        sa.Column('current_period_end', sa.DateTime),
        sa.Column('trial_end', sa.DateTime),
        sa.Column('limits', postgresql.JSONB, default={}),  # Usage limits per period
        sa.Column('usage', postgresql.JSONB, default={}),  # Current usage stats
        sa.Column('payment_provider', sa.String(50)),  # alipay, wechat, stripe
        sa.Column('payment_id', sa.String(200)),  # External payment reference
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('canceled_at', sa.DateTime)
    )
    
    # Create indexes for subscriptions
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'])
    
    # Create audit_logs table for tracking important events
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=generate_uuid),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('action', sa.String(100), nullable=False),  # create, update, delete, login, etc.
        sa.Column('resource_type', sa.String(50)),  # knowledge_base, document, conversation, etc.
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('details', postgresql.JSONB, default={}),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade():
    """Drop all tables"""
    op.drop_index('ix_audit_logs_resource', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index('ix_subscriptions_plan_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_index('ix_conversations_session_id', table_name='conversations')
    op.drop_index('ix_conversations_kb_id', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('ix_documents_file_hash', table_name='documents')
    op.drop_index('ix_documents_status', table_name='documents')
    op.drop_index('ix_documents_kb_id', table_name='documents')
    op.drop_table('documents')
    
    op.drop_index('ix_knowledge_bases_vector_collection', table_name='knowledge_bases')
    op.drop_index('ix_knowledge_bases_user_id', table_name='knowledge_bases')
    op.drop_table('knowledge_bases')
    
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')