"""Initial database schema

Revision ID: initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create analysis_results table
    op.create_table('analysis_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, default='en'),
        sa.Column('poetic_form', sa.String(length=100), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('technical_craft_score', sa.Float(), nullable=True),
        sa.Column('language_diction_score', sa.Float(), nullable=True),
        sa.Column('imagery_voice_score', sa.Float(), nullable=True),
        sa.Column('emotional_impact_score', sa.Float(), nullable=True),
        sa.Column('cultural_fidelity_score', sa.Float(), nullable=True),
        sa.Column('originality_score', sa.Float(), nullable=True),
        sa.Column('quantitative_metrics', sa.JSON(), nullable=True),
        sa.Column('prosody_analysis', sa.JSON(), nullable=True),
        sa.Column('literary_devices', sa.JSON(), nullable=True),
        sa.Column('sentiment_analysis', sa.JSON(), nullable=True),
        sa.Column('evaluation', sa.JSON(), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('strictness_level', sa.Integer(), nullable=True, default=8),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('line_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes
    op.create_index('idx_uuid', 'analysis_results', ['uuid'], unique=False)
    op.create_index('idx_created_at', 'analysis_results', ['created_at'], unique=False)
    op.create_index('idx_language_created', 'analysis_results', ['language', 'created_at'], unique=False)
    op.create_index('idx_overall_score', 'analysis_results', ['overall_score'], unique=False)
    op.create_index('idx_form', 'analysis_results', ['poetic_form'], unique=False)
    
    # Create database_stats table
    op.create_table('database_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stat_name', sa.String(length=100), nullable=False),
        sa.Column('stat_value', sa.JSON(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stat_name')
    )
    
    # Create user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('setting_key', sa.String(length=100), nullable=False),
        sa.Column('setting_value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('setting_key')
    )


def downgrade() -> None:
    op.drop_index('idx_form', table_name='analysis_results')
    op.drop_index('idx_overall_score', table_name='analysis_results')
    op.drop_index('idx_language_created', table_name='analysis_results')
    op.drop_index('idx_created_at', table_name='analysis_results')
    op.drop_index('idx_uuid', table_name='analysis_results')
    
    op.drop_table('user_settings')
    op.drop_table('database_stats')
    op.drop_table('analysis_results')
