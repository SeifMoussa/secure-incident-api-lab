from sqlalchemy.orm import Session

from app.common.enums import IncidentSeverity, IncidentStatus
from app.incidents.models import Incident


def create_synthetic_incident(
    db_session: Session,
    *,
    created_by: str,
    title: str = "Synthetic incident",
    description: str = "Synthetic defensive incident for test-only use.",
    severity: IncidentSeverity = IncidentSeverity.MEDIUM,
    status: IncidentStatus = IncidentStatus.OPEN,
    assigned_to: str | None = None,
    tags: list[str] | None = None,
) -> Incident:
    incident = Incident(
        title=title,
        description=description,
        severity=severity,
        status=status,
        created_by=created_by,
        assigned_to=assigned_to,
        tags=tags or [],
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident
