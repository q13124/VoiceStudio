from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251021_init_ab_eval"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ab_summary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=255), nullable=False, index=True),
        sa.Column("engine", sa.String(length=128), nullable=False, index=True),
        sa.Column("n_items", sa.Integer(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("win_rate", sa.Float(), nullable=False),
        sa.Column("ci_low", sa.Float(), nullable=True),
        sa.Column("ci_high", sa.Float(), nullable=True),
        sa.Column("mean_score", sa.Float(), nullable=True),
        sa.Column("median_lufs", sa.Float(), nullable=True),
        sa.Column("clip_hit_rate", sa.Float(), nullable=True),
        sa.Column(
            "created_utc",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_table(
        "eval_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(length=255), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("engine", sa.String(length=128), nullable=False, index=True),
        sa.Column("wr", sa.Float(), nullable=False),
        sa.Column("latency_p50", sa.Float(), nullable=True),
        sa.Column("latency_p95", sa.Float(), nullable=True),
        sa.Column("clip_rate", sa.Float(), nullable=True),
        sa.Column("lufs_med", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("eval_runs")
    op.drop_table("ab_summary")
