from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.auth.models import User
from app.common.enums import AuditAction, AuditOutcome


def test_audit_enum_values_are_correct() -> None:
    assert [action.value for action in AuditAction] == [
        "CREATE",
        "UPDATE",
        "DELETE",
        "LOGIN",
        "LOGOUT",
    ]
    assert [outcome.value for outcome in AuditOutcome] == ["SUCCESS", "FAILURE"]


def test_audit_log_model_fields_exist() -> None:
    columns = set(AuditLog.__table__.columns.keys())

    assert {
        "audit_id",
        "actor_id",
        "action",
        "resource_type",
        "resource_id",
        "timestamp",
        "ip_address",
        "changes",
        "outcome",
    } <= columns


def test_audit_log_json_changes_work(db_session: Session) -> None:
    user = User(
        email="audit-user@example.com",
        display_name="Synthetic Audit User",
        password_hash="synthetic-hash-only",
    )
    db_session.add(user)
    db_session.flush()
    audit_log = AuditLog(
        actor_id=user.user_id,
        action=AuditAction.CREATE,
        resource_type="incident",
        resource_id="synthetic-resource-id",
        ip_address="127.0.0.1",
        changes={"safe_field": {"old": None, "new": "synthetic"}},
        outcome=AuditOutcome.SUCCESS,
    )

    db_session.add(audit_log)
    db_session.commit()
    db_session.refresh(audit_log)

    assert audit_log.audit_id
    assert audit_log.changes["safe_field"]["new"] == "synthetic"
    assert audit_log.timestamp is not None


def test_audit_log_has_no_update_delete_router_created() -> None:
    assert AuditLog.__tablename__ == "audit_log"
    assert not hasattr(AuditLog, "update_endpoint")
    assert not hasattr(AuditLog, "delete_endpoint")
