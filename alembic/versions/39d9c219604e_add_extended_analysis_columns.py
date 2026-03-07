"""add_extended_analysis_columns

Revision ID: 39d9c219604e
Revises: 2324ea6d53fe
Create Date: 2026-03-06 20:41:58.607271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39d9c219604e'
down_revision: Union[str, None] = '2324ea6d53fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('analysis_results', sa.Column('theory_analysis', sa.JSON(), nullable=True))
    op.add_column('analysis_results', sa.Column('structural_analysis', sa.JSON(), nullable=True))
    op.add_column('analysis_results', sa.Column('stylometry_data', sa.JSON(), nullable=True))
    op.add_column('analysis_results', sa.Column('competition_rubrics_data', sa.JSON(), nullable=True))
    op.add_column('analysis_results', sa.Column('evolutionary_data', sa.JSON(), nullable=True))
    op.add_column('analysis_results', sa.Column('educational_insight', sa.Text(), nullable=True))
    # Note: user_settings.uuid was already added in migration v2 (2324ea6d53fe).
    # op.alter_column omitted because SQLite does not support ALTER COLUMN.


def downgrade() -> None:
    op.drop_column('analysis_results', 'educational_insight')
    op.drop_column('analysis_results', 'evolutionary_data')
    op.drop_column('analysis_results', 'competition_rubrics_data')
    op.drop_column('analysis_results', 'stylometry_data')
    op.drop_column('analysis_results', 'structural_analysis')
    op.drop_column('analysis_results', 'theory_analysis')
