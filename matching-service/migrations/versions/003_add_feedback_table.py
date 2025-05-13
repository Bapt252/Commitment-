"""Add feedback table

Revision ID: 003
Create Date: 2025-04-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM


def upgrade():
    # Créer l'enum pour match_quality
    match_quality_enum = ENUM(
        'VERY_GOOD', 'GOOD', 'MEDIUM', 'POOR', 'UNACCEPTABLE',
        name='match_quality_type',
        create_type=True
    )
    
    op.create_table(
        'match_feedbacks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('match_id', UUID(as_uuid=True), sa.ForeignKey('match_results.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_type', sa.String(20), nullable=False),  # 'recruiter' ou 'candidate'
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('match_quality', match_quality_enum, nullable=False),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('algorithm_version', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        
        # Contraintes
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),
        sa.UniqueConstraint('match_id', 'user_id', name='unique_feedback_per_user_per_match'),
        sa.Index('idx_match_feedbacks_match_id', 'match_id'),
        sa.Index('idx_match_feedbacks_user_id', 'user_id'),
        sa.Index('idx_match_feedbacks_created_at', 'created_at')
    )

def downgrade():
    op.drop_table('match_feedbacks')
    op.execute('DROP TYPE IF EXISTS match_quality_type')