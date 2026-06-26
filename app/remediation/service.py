"""Remediation task service-layer operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import RemediationStatus
from app.common.models import utc_now
from app.common.pagination import PaginationParams
from app.incidents.models import Incident
from app.remediation.models import RemediationTask
from app.remediation.schemas import (
    RemediationCreateRequest,
    RemediationDeleteResponse,
    RemediationListResponse,
    RemediationResponse,
    RemediationUpdateRequest,
)


class RemediationServiceError(ValueError):
    """Raised for expected safe remediation workflow failures."""


def create_remediation(
    db: Session,
    *,
    incident_id: str,
    payload: RemediationCreateRequest,
) -> RemediationResponse:
    _get_active_incident_or_raise(db, incident_id)
    _validate_active_user(db, payload.owner)
    task = RemediationTask(
        incident_id=incident_id,
        action=payload.action,
        owner=payload.owner,
        status=payload.status,
        deadline=payload.deadline,
        completion_notes=payload.completion_notes,
        completed_at=utc_now() if payload.status == RemediationStatus.COMPLETE else None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return remediation_response(task)


def list_remediation(
    db: Session,
    *,
    incident_id: str,
    pagination: PaginationParams,
) -> RemediationListResponse:
    _get_active_incident_or_raise(db, incident_id)
    query = select(RemediationTask).where(
        RemediationTask.incident_id == incident_id,
        RemediationTask.is_deleted.is_(False),
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    tasks = db.scalars(
        query.order_by(RemediationTask.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return RemediationListResponse(
        items=[remediation_response(task) for task in tasks],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def update_remediation(
    db: Session,
    *,
    incident_id: str,
    task_id: str,
    payload: RemediationUpdateRequest,
) -> RemediationResponse:
    task = _get_active_task_or_raise(db, incident_id, task_id)
    data = payload.model_dump(exclude_unset=True)
    if "owner" in data:
        _validate_active_user(db, data["owner"])
    for field_name, value in data.items():
        setattr(task, field_name, value)
    if "status" in data:
        task.completed_at = utc_now() if task.status == RemediationStatus.COMPLETE else None
    task.updated_at = utc_now()
    db.commit()
    db.refresh(task)
    return remediation_response(task)


def soft_delete_remediation(
    db: Session, *, incident_id: str, task_id: str
) -> RemediationDeleteResponse:
    task = _get_active_task_or_raise(db, incident_id, task_id)
    task.is_deleted = True
    task.updated_at = utc_now()
    db.commit()
    db.refresh(task)
    return RemediationDeleteResponse(
        message="Remediation task deleted.", task=remediation_response(task)
    )


def remediation_response(task: RemediationTask) -> RemediationResponse:
    return RemediationResponse(
        task_id=task.task_id,
        incident_id=task.incident_id,
        action=task.action,
        owner=task.owner,
        status=task.status,
        deadline=task.deadline.isoformat() if task.deadline else None,
        completion_notes=task.completion_notes,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        is_deleted=task.is_deleted,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


def _get_active_incident_or_raise(db: Session, incident_id: str) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None or incident.is_deleted:
        msg = "Incident not found."
        raise RemediationServiceError(msg)
    return incident


def _get_active_task_or_raise(db: Session, incident_id: str, task_id: str) -> RemediationTask:
    _get_active_incident_or_raise(db, incident_id)
    task = db.get(RemediationTask, task_id)
    if task is None or task.is_deleted or task.incident_id != incident_id:
        msg = "Remediation task not found."
        raise RemediationServiceError(msg)
    return task


def _validate_active_user(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        msg = "Owner not found."
        raise RemediationServiceError(msg)
