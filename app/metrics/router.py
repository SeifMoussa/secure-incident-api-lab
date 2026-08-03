"""Metrics API route."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import Role
from app.database import get_db
from app.metrics.service import compute_incident_metrics, render_prometheus_text

router = APIRouter(tags=["metrics"])

read_metrics = require_any_role(Role.ADMIN, Role.AUDITOR)


@router.get("/metrics", response_class=PlainTextResponse)
def get_metrics_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(read_metrics)],
) -> PlainTextResponse:
    _ = current_user
    snapshot = compute_incident_metrics(db)
    return PlainTextResponse(
        render_prometheus_text(snapshot),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
