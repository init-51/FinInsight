"""create backtest_results table

Revision ID: 20241022_create_backtest_results
Revises: 
Create Date: 2025-10-22 10:50:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20241022_create_backtest_results"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "backtest_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("portfolio_name", sa.String(), nullable=False),
        sa.Column("final_value", sa.Float(), nullable=False),
        sa.Column("cumulative_return", sa.Float(), nullable=False),
        sa.Column("volatility", sa.Float(), nullable=False),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("timeseries", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_backtest_results_job_id", "backtest_results", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_backtest_results_job_id", table_name="backtest_results")
    op.drop_table("backtest_results")
