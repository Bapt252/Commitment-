"""create ab testing tables

Revision ID: 001
Create Date: 2024-04-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create experiments table
    op.create_table('experiments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('traffic_allocation', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create experiment_metrics table
    op.create_table('experiment_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('experiment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('variant', sa.String(length=50), nullable=False),
        sa.Column('match_count', sa.Integer(), nullable=True),
        sa.Column('feedback_score', sa.Float(), nullable=True),
        sa.Column('conversion_count', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_experiments_status', 'experiments', ['status'], unique=False)
    op.create_index('idx_experiment_metrics_user', 'experiment_metrics', ['user_id'], unique=False)
    op.create_index('idx_experiment_metrics_experiment', 'experiment_metrics', ['experiment_id'], unique=False)

def downgrade():
    op.drop_index('idx_experiment_metrics_experiment', table_name='experiment_metrics')
    op.drop_index('idx_experiment_metrics_user', table_name='experiment_metrics')
    op.drop_index('idx_experiments_status', table_name='experiments')
    op.drop_table('experiment_metrics')
    op.drop_table('experiments')