"""Audit read API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.schemas import AuditFilterParams, AuditListResponse
from app.audit.service import list_audit_entries
from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import AuditAction, AuditOutcome, Role
from app.common.pagination import PaginationParams, get_pagination_params
from app.database import get_db

router = APIRouter(prefix="/audit", tags=["audit"])

read_audit = require_any_role(Role.ADMIN, Role.AUDITOR)


@router.get("/", response_model=AuditListResponse)
def list_audit_route(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_user: Annotated[User, Depends(read_audit)],
    resource_type: str | None = None,
    resource_id: str | None = None,
    actor: str | None = None,
    action: AuditAction | None = None,
    outcome: AuditOutcome | None = None,
) -> AuditListResponse:
    _ = current_user
    filters = AuditFilterParams(
        resource_type=resource_type,
        resource_id=resource_id,
        actor=actor,
        action=action,
        outcome=outcome,
    )
    return list_audit_entries(db, filters=filters, pagination=pagination)
