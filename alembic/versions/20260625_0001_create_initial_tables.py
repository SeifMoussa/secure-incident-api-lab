"""create initial tables

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260625_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Alembic discovers these required revision identifiers by module-level name.
# This internal read documents that contract for static analysis without changing
# migration behavior.
_unused_alembic_revision_identifiers = (revision, down_revision, branch_labels, depends_on)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "ANALYST", "VIEWER", "AUDITOR", native_enum=False, length=7),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "token_blocklist",
        sa.Column("token_id", sa.String(length=36), nullable=False),
        sa.Column("jti", sa.String(length=128), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("token_id"),
    )
    op.create_index(op.f("ix_token_blocklist_jti"), "token_blocklist", ["jti"], unique=True)
    op.create_index("ix_token_blocklist_jti_unique", "token_blocklist", ["jti"], unique=True)

    op.create_table(
        "incidents",
        sa.Column("incident_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", native_enum=False, length=8),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "OPEN",
                "IN_PROGRESS",
                "CONTAINED",
                "RESOLVED",
                "CLOSED",
                native_enum=False,
                length=11,
            ),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("assigned_to", sa.String(length=36), nullable=True),
        sa.Column("mitre_tactic", sa.String(length=120), nullable=True),
        sa.Column("mitre_technique", sa.String(length=120), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("incident_id"),
    )

    op.create_table(
        "audit_log",
        sa.Column("audit_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column(
            "action",
            sa.Enum("CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", native_enum=False, length=6),
            nullable=False,
        ),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum("SUCCESS", "FAILURE", native_enum=False, length=7),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("audit_id"),
    )

    op.create_table(
        "tickets",
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("incident_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "IN_PROGRESS", "DONE", "BLOCKED", native_enum=False, length=11),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("P1", "P2", "P3", "P4", native_enum=False, length=2),
            nullable=False,
        ),
        sa.Column("assigned_to", sa.String(length=36), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.incident_id"]),
        sa.PrimaryKeyConstraint("ticket_id"),
    )

    op.create_table(
        "evidence_notes",
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.Column("incident_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.incident_id"]),
        sa.PrimaryKeyConstraint("evidence_id"),
    )

    op.create_table(
        "remediation_tasks",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("incident_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=36), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETE", "SKIPPED", native_enum=False, length=11),
            nullable=False,
        ),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.incident_id"]),
        sa.ForeignKeyConstraint(["owner"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("task_id"),
    )

    op.create_table(
        "evidence_attachments",
        sa.Column("attachment_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_reference", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence_notes.evidence_id"]),
        sa.PrimaryKeyConstraint("attachment_id"),
    )


def downgrade() -> None:
    op.drop_table("evidence_attachments")
    op.drop_table("remediation_tasks")
    op.drop_table("evidence_notes")
    op.drop_table("tickets")
    op.drop_table("audit_log")
    op.drop_table("incidents")
    op.drop_index("ix_token_blocklist_jti_unique", table_name="token_blocklist")
    op.drop_index(op.f("ix_token_blocklist_jti"), table_name="token_blocklist")
    op.drop_table("token_blocklist")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
