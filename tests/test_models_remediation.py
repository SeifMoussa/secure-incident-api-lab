from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import IncidentSeverity, IncidentStatus, RemediationStatus
from app.incidents.models import Incident
from app.remediation.models import RemediationTask


def test_remediation_status_enum_values_are_correct() -> None:
    assert [status.value for status in RemediationStatus] == [
        "PENDING",
        "IN_PROGRESS",
        "COMPLETE",
        "SKIPPED",
    ]


def test_remediation_task_model_fields_exist() -> None:
    columns = set(RemediationTask.__table__.columns.keys())

    assert {
        "task_id",
        "incident_id",
        "action",
        "owner",
        "status",
        "deadline",
        "completion_notes",
        "completed_at",
        "is_deleted",
        "created_at",
        "updated_at",
    } <= columns


def test_remediation_task_relationship_and_completion_fields(db_session: Session) -> None:
    user = User(
        email="remediation-user@example.com",
        display_name="Synthetic Remediation User",
        password_hash="synthetic-hash-only",
    )
    db_session.add(user)
    db_session.flush()
    incident = Incident(
        title="Synthetic incident",
        description="Synthetic defensive incident record.",
        severity=IncidentSeverity.CRITICAL,
        status=IncidentStatus.CONTAINED,
        created_by=user.user_id,
    )
    db_session.add(incident)
    db_session.flush()
    task = RemediationTask(
        incident_id=incident.incident_id,
        action="Document synthetic containment action.",
        owner=user.user_id,
        status=RemediationStatus.COMPLETE,
        deadline=datetime.now(UTC) + timedelta(days=1),
        completed_at=datetime.now(UTC),
        completion_notes="Synthetic completion note.",
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(incident)

    assert incident.remediation_tasks[0].status == RemediationStatus.COMPLETE
    assert incident.remediation_tasks[0].completed_at is not None
    assert incident.remediation_tasks[0].is_deleted is False
