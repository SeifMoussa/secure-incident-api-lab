"""add incident sla timestamps

Revision ID: 20260803_0002
Revises: 20260625_0001
Create Date: 2026-08-03
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260803_0002"
down_revision: str | None = "20260625_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Alembic discovers these required revision identifiers by module-level name.
# This internal read documents that contract for static analysis without changing
# migration behavior.
_unused_alembic_revision_identifiers = (revision, down_revision, branch_labels, depends_on)


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column(
            "status_changed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "incidents",
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    with op.batch_alter_table("incidents") as batch_op:
        batch_op.alter_column("status_changed_at", server_default=None)


def downgrade() -> None:
    op.drop_column("incidents", "resolved_at")
    op.drop_column("incidents", "acknowledged_at")
    op.drop_column("incidents", "status_changed_at")
