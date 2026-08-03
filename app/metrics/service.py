"""Incident metrics computation for Prometheus-style scraping."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import IncidentSeverity, IncidentStatus
from app.common.models import utc_now
from app.incidents.models import Incident
from app.incidents.sla import (
    age_in_status_seconds,
    seconds_between,
    time_to_acknowledge_seconds,
    time_to_resolve_seconds,
)

# Illustrative SLA thresholds for this lab, not a real incident-response policy.
ACKNOWLEDGEMENT_BREACH_SECONDS = 4 * 60 * 60
RESOLUTION_BREACH_SECONDS = 72 * 60 * 60


@dataclass(frozen=True)
class IncidentMetricsSnapshot:
    """A point-in-time snapshot of incident volume and SLA metrics."""

    counts_by_status: dict[str, int]
    counts_by_severity: dict[str, int]
    acknowledged_count: int
    resolved_count: int
    average_time_to_acknowledge_seconds: float | None
    average_time_to_resolve_seconds: float | None
    breaching_acknowledgement_count: int
    breaching_resolution_count: int


def compute_incident_metrics(db: Session) -> IncidentMetricsSnapshot:
    """Compute incident volume and SLA metrics from active (non-deleted) incidents."""
    incidents = db.scalars(select(Incident).where(Incident.is_deleted.is_(False))).all()
    now = utc_now()

    counts_by_status = {status.value: 0 for status in IncidentStatus}
    counts_by_severity = {severity.value: 0 for severity in IncidentSeverity}
    ack_durations: list[float] = []
    resolve_durations: list[float] = []
    acknowledged_count = 0
    resolved_count = 0
    breaching_ack = 0
    breaching_resolve = 0

    for incident in incidents:
        counts_by_status[incident.status.value] += 1
        counts_by_severity[incident.severity.value] += 1

        ack_seconds = time_to_acknowledge_seconds(incident)
        if ack_seconds is not None:
            acknowledged_count += 1
            ack_durations.append(ack_seconds)
        elif age_in_status_seconds(incident, now=now) >= ACKNOWLEDGEMENT_BREACH_SECONDS:
            breaching_ack += 1

        resolve_seconds = time_to_resolve_seconds(incident)
        if resolve_seconds is not None:
            resolved_count += 1
            resolve_durations.append(resolve_seconds)
        elif seconds_between(incident.created_at, now) >= RESOLUTION_BREACH_SECONDS:
            breaching_resolve += 1

    return IncidentMetricsSnapshot(
        counts_by_status=counts_by_status,
        counts_by_severity=counts_by_severity,
        acknowledged_count=acknowledged_count,
        resolved_count=resolved_count,
        average_time_to_acknowledge_seconds=_average(ack_durations),
        average_time_to_resolve_seconds=_average(resolve_durations),
        breaching_acknowledgement_count=breaching_ack,
        breaching_resolution_count=breaching_resolve,
    )


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def render_prometheus_text(snapshot: IncidentMetricsSnapshot) -> str:
    """Render a metrics snapshot in Prometheus text exposition format."""
    lines: list[str] = []

    lines.append("# HELP incidents_by_status_total Current non-deleted incidents by status.")
    lines.append("# TYPE incidents_by_status_total gauge")
    for status_value, count in snapshot.counts_by_status.items():
        lines.append(f'incidents_by_status_total{{status="{status_value}"}} {count}')

    lines.append("# HELP incidents_by_severity_total Current non-deleted incidents by severity.")
    lines.append("# TYPE incidents_by_severity_total gauge")
    for severity_value, count in snapshot.counts_by_severity.items():
        lines.append(f'incidents_by_severity_total{{severity="{severity_value}"}} {count}')

    lines.append("# HELP incident_sla_acknowledged_total Incidents that have been acknowledged.")
    lines.append("# TYPE incident_sla_acknowledged_total gauge")
    lines.append(f"incident_sla_acknowledged_total {snapshot.acknowledged_count}")

    lines.append("# HELP incident_sla_resolved_total Incidents currently resolved or closed.")
    lines.append("# TYPE incident_sla_resolved_total gauge")
    lines.append(f"incident_sla_resolved_total {snapshot.resolved_count}")

    lines.append(
        "# HELP incident_sla_time_to_acknowledge_seconds_avg "
        "Average seconds from creation to first acknowledgement."
    )
    lines.append("# TYPE incident_sla_time_to_acknowledge_seconds_avg gauge")
    lines.append(
        "incident_sla_time_to_acknowledge_seconds_avg "
        f"{_format_optional(snapshot.average_time_to_acknowledge_seconds)}"
    )

    lines.append(
        "# HELP incident_sla_time_to_resolve_seconds_avg "
        "Average seconds from creation to resolution."
    )
    lines.append("# TYPE incident_sla_time_to_resolve_seconds_avg gauge")
    lines.append(
        "incident_sla_time_to_resolve_seconds_avg "
        f"{_format_optional(snapshot.average_time_to_resolve_seconds)}"
    )

    lines.append(
        "# HELP incident_sla_breaching_acknowledgement_total "
        "Unacknowledged incidents older than the illustrative acknowledgement threshold."
    )
    lines.append("# TYPE incident_sla_breaching_acknowledgement_total gauge")
    lines.append(
        f"incident_sla_breaching_acknowledgement_total {snapshot.breaching_acknowledgement_count}"
    )

    lines.append(
        "# HELP incident_sla_breaching_resolution_total "
        "Unresolved incidents older than the illustrative resolution threshold."
    )
    lines.append("# TYPE incident_sla_breaching_resolution_total gauge")
    lines.append(f"incident_sla_breaching_resolution_total {snapshot.breaching_resolution_count}")

    return "\n".join(lines) + "\n"


def _format_optional(value: float | None) -> str:
    return "NaN" if value is None else str(value)
