from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import IncidentSeverity, IncidentStatus
from app.incidents.models import Incident


def test_incident_enum_values_are_correct() -> None:
    assert [severity.value for severity in IncidentSeverity] == [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ]
    assert [status.value for status in IncidentStatus] == [
        "OPEN",
        "IN_PROGRESS",
        "CONTAINED",
        "RESOLVED",
        "CLOSED",
    ]


def test_incident_model_fields_exist() -> None:
    columns = set(Incident.__table__.columns.keys())

    assert {
        "incident_id",
        "title",
        "description",
        "severity",
        "status",
        "created_by",
        "assigned_to",
        "mitre_tactic",
        "mitre_technique",
        "tags",
        "is_deleted",
        "created_at",
        "updated_at",
    } <= columns


def test_incident_json_tags_and_soft_delete_defaults_work(db_session: Session) -> None:
    user = User(
        email="incident-creator@example.com",
        display_name="Synthetic Creator",
        password_hash="synthetic-hash-only",
    )
    db_session.add(user)
    db_session.flush()

    incident = Incident(
        title="Synthetic incident",
        description="Synthetic defensive incident record.",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.OPEN,
        created_by=user.user_id,
        tags=["synthetic", "defensive"],
    )

    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    assert incident.tags == ["synthetic", "defensive"]
    assert incident.is_deleted is False
    assert incident.creator.email == "incident-creator@example.com"
