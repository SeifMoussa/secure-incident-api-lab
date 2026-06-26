"""ADMIN-only user management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.admin.schemas import (
    AdminDeactivateResponse,
    AdminRoleUpdateRequest,
    AdminUserListResponse,
    AdminUserResponse,
)
from app.admin.service import (
    AdminServiceError,
    deactivate_user,
    get_user_detail,
    list_users,
    update_user_role,
)
from app.auth.models import User
from app.common.dependencies import require_admin
from app.common.pagination import PaginationParams, get_pagination_params
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users/", response_model=AdminUserListResponse)
def list_admin_users(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> AdminUserListResponse:
    _ = current_admin
    return list_users(db, pagination)


@router.get("/users/{uid}", response_model=AdminUserResponse)
def get_admin_user(
    uid: str,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> AdminUserResponse:
    _ = current_admin
    try:
        return get_user_detail(db, uid)
    except AdminServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/users/{uid}/role", response_model=AdminUserResponse)
def update_admin_user_role(
    uid: str,
    payload: AdminRoleUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> AdminUserResponse:
    try:
        return update_user_role(db, actor=current_admin, user_id=uid, role=payload.role)
    except AdminServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/users/{uid}", response_model=AdminDeactivateResponse)
def deactivate_admin_user(
    uid: str,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> AdminDeactivateResponse:
    try:
        return deactivate_user(db, actor=current_admin, user_id=uid)
    except AdminServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
