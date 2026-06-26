"""ADMIN-only user management service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.admin.schemas import AdminDeactivateResponse, AdminUserListResponse, AdminUserResponse
from app.auth.models import User
from app.common.enums import Role
from app.common.models import utc_now
from app.common.pagination import PaginationParams


class AdminServiceError(ValueError):
    """Raised for expected safe admin-management failures."""


def list_users(db: Session, pagination: PaginationParams) -> AdminUserListResponse:
    """Return a safe paginated user list."""
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(
        select(User)
        .order_by(User.created_at.desc(), User.email.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return AdminUserListResponse(
        items=[admin_user_response(user) for user in users],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def get_user_detail(db: Session, user_id: str) -> AdminUserResponse:
    """Return one safe user profile for admin review."""
    return admin_user_response(_get_user_or_raise(db, user_id))


def update_user_role(
    db: Session,
    *,
    actor: User,
    user_id: str,
    role: Role,
) -> AdminUserResponse:
    """Update another user's role, preventing accidental self-lockout."""
    target_user = _get_user_or_raise(db, user_id)
    if target_user.user_id == actor.user_id and role != actor.role:
        msg = "Admins cannot change their own role."
        raise AdminServiceError(msg)

    target_user.role = role
    target_user.updated_at = utc_now()
    db.commit()
    db.refresh(target_user)
    return admin_user_response(target_user)


def deactivate_user(db: Session, *, actor: User, user_id: str) -> AdminDeactivateResponse:
    """Deactivate another user without hard deletion."""
    target_user = _get_user_or_raise(db, user_id)
    if target_user.user_id == actor.user_id:
        msg = "Admins cannot deactivate their own account."
        raise AdminServiceError(msg)

    target_user.is_active = False
    target_user.updated_at = utc_now()
    db.commit()
    db.refresh(target_user)
    return AdminDeactivateResponse(
        message="User deactivated.",
        user=admin_user_response(target_user),
    )


def admin_user_response(user: User) -> AdminUserResponse:
    """Return a user response without password or token fields."""
    return AdminUserResponse(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


def _get_user_or_raise(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        msg = "User not found."
        raise AdminServiceError(msg)
    return user
