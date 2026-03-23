"""
Add quality inspection tables

Revision ID: 002_quality_inspections
Revises: 001_initial
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_quality_inspections'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Add quality inspection tables"""
    
    # Create quality_rules table
    op.create_table(
        'quality_rules',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('condition', sa.Text, nullable=False),
        sa.Column('score_impact', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Create quality_inspections table
    op.create_table(
        'quality_inspections',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id'), nullable=True),
        sa.Column('inspection_type', sa.String(50), default='auto'),
        sa.Column('response_time_seconds', sa.Float, default=0.0),
        sa.Column('keywords_detected', sa.Text, default='[]'),
        sa.Column('quality_score', sa.Integer, default=0),
        sa.Column('has_issues', sa.Boolean, default=False),
        sa.Column('issues_found', sa.Text, default='[]'),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Create indexes
    op.create_index('ix_quality_inspections_conversation_id', 'quality_inspections', ['conversation_id'])
    op.create_index('ix_quality_inspections_message_id', 'quality_inspections', ['message_id'])
    op.create_index('ix_quality_inspections_created_at', 'quality_inspections', ['created_at'])
    op.create_index('ix_quality_inspections_score', 'quality_inspections', ['quality_score'])
    op.create_index('ix_quality_rules_type', 'quality_rules', ['rule_type'])
    op.create_index('ix_quality_rules_active', 'quality_rules', ['is_active'])


def downgrade():
    """Drop quality inspection tables"""
    op.drop_index('ix_quality_inspections_score', table_name='quality_inspections')
    op.drop_index('ix_quality_inspections_created_at', table_name='quality_inspections')
    op.drop_index('ix_quality_inspections_message_id', table_name='quality_inspections')
    op.drop_index('ix_quality_inspections_conversation_id', table_name='quality_inspections')
    op.drop_table('quality_inspections')
    
    op.drop_index('ix_quality_rules_active', table_name='quality_rules')
    op.drop_index('ix_quality_rules_type', table_name='quality_rules')
    op.drop_table('quality_rules')