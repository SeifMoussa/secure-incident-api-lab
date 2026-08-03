"""Incident SLA calculation helpers."""

from datetime import datetime

from app.common.enums import IncidentStatus
from app.common.models import utc_now
from app.incidents.models import Incident

RESOLVED_STATUSES = frozenset({IncidentStatus.RESOLVED, IncidentStatus.CLOSED})


def seconds_between(earlier: datetime, later: datetime) -> float:
    """Difference in seconds, tolerating SQLite's loss of tzinfo on read-back.

    All timestamps on this model are written as UTC, so it's safe to drop tzinfo before
    subtracting rather than requiring both sides to be aware or both naive.
    """
    if earlier.tzinfo is not None:
        earlier = earlier.replace(tzinfo=None)
    if later.tzinfo is not None:
        later = later.replace(tzinfo=None)
    return (later - earlier).total_seconds()


def time_to_acknowledge_seconds(incident: Incident) -> float | None:
    """Seconds between creation and first acknowledgement, or None if not yet acknowledged."""
    if incident.acknowledged_at is None:
        return None
    return seconds_between(incident.created_at, incident.acknowledged_at)


def time_to_resolve_seconds(incident: Incident) -> float | None:
    """Seconds between creation and resolution, or None if not currently resolved."""
    if incident.resolved_at is None:
        return None
    return seconds_between(incident.created_at, incident.resolved_at)


def age_in_status_seconds(incident: Incident, *, now: datetime | None = None) -> float:
    """Seconds since the incident's status last changed."""
    reference = now or utc_now()
    return seconds_between(incident.status_changed_at, reference)


def apply_status_transition_timestamps(
    incident: Incident,
    *,
    previous_status: IncidentStatus,
    new_status: IncidentStatus,
    now: datetime | None = None,
) -> None:
    """Update status_changed_at/acknowledged_at/resolved_at for a status transition.

    No-op if the status did not actually change. acknowledged_at is a one-time stamp: once an
    incident leaves OPEN it stays acknowledged even if it is later reopened. resolved_at tracks
    current resolution state, so reopening a resolved incident clears it.
    """
    if new_status == previous_status:
        return
    reference = now or utc_now()
    incident.status_changed_at = reference
    if new_status != IncidentStatus.OPEN and incident.acknowledged_at is None:
        incident.acknowledged_at = reference
    incident.resolved_at = reference if new_status in RESOLVED_STATUSES else None
