from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_admin_and_auditor_can_read_metrics(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="metrics-admin@example.com", role=Role.ADMIN)
    auditor = create_synthetic_user(
        db_session, email="metrics-auditor@example.com", role=Role.AUDITOR
    )

    assert client.get("/metrics", headers=bearer_header(test_settings, admin)).status_code == 200
    assert client.get("/metrics", headers=bearer_header(test_settings, auditor)).status_code == 200


def test_non_metrics_roles_and_missing_token_cannot_read_metrics(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    for role in [Role.ANALYST, Role.VIEWER]:
        user = create_synthetic_user(
            db_session, email=f"metrics-deny-{role.value.lower()}@example.com", role=role
        )
        assert client.get("/metrics", headers=bearer_header(test_settings, user)).status_code == 403
    assert client.get("/metrics").status_code == 401


def test_metrics_response_is_prometheus_text_format(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="metrics-format-admin@example.com", role=Role.ADMIN
    )

    response = client.get("/metrics", headers=bearer_header(test_settings, admin))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "# HELP incidents_by_status_total" in body
    assert "# TYPE incidents_by_status_total gauge" in body
    assert 'incidents_by_status_total{status="OPEN"}' in body
    assert "incident_sla_acknowledged_total" in body
    assert "incident_sla_resolved_total" in body
    assert "incident_sla_time_to_acknowledge_seconds_avg" in body
    assert "incident_sla_time_to_resolve_seconds_avg" in body
    assert "incident_sla_breaching_acknowledgement_total" in body
    assert "incident_sla_breaching_resolution_total" in body


def test_metrics_reflect_incident_counts_by_status(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="metrics-counts-admin@example.com", role=Role.ADMIN
    )
    create_synthetic_incident(db_session, created_by=admin.user_id)
    create_synthetic_incident(db_session, created_by=admin.user_id)

    response = client.get("/metrics", headers=bearer_header(test_settings, admin))
    body = response.text

    assert 'incidents_by_status_total{status="OPEN"} 2' in body
    assert "incident_sla_acknowledged_total 0" in body
    assert "incident_sla_resolved_total 0" in body


def test_metrics_reports_averages_once_incidents_are_acknowledged_and_resolved(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="metrics-avg-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    client.patch(
        f"/incidents/{incident.incident_id}",
        json={"status": "RESOLVED"},
        headers=bearer_header(test_settings, admin),
    )

    response = client.get("/metrics", headers=bearer_header(test_settings, admin))
    lines = response.text.splitlines()

    def metric_value(name: str) -> str:
        (line,) = [line for line in lines if line.startswith(f"{name} ")]
        return line.split(" ", 1)[1]

    assert "incident_sla_acknowledged_total 1" in response.text
    assert "incident_sla_resolved_total 1" in response.text
    assert float(metric_value("incident_sla_time_to_acknowledge_seconds_avg")) >= 0
    assert float(metric_value("incident_sla_time_to_resolve_seconds_avg")) >= 0


def test_metrics_excludes_soft_deleted_incidents(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="metrics-deleted-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    client.delete(
        f"/incidents/{incident.incident_id}",
        headers=bearer_header(test_settings, admin),
    )

    response = client.get("/metrics", headers=bearer_header(test_settings, admin))
    body = response.text

    assert 'incidents_by_status_total{status="OPEN"} 0' in body
