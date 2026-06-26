"""Reusable authentication and authorization dependencies."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.common.enums import Role
from app.common.permissions import ADMIN_USER_MANAGEMENT_ROLES


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the current active user from the database."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(role: Role) -> Callable[[User], User]:
    """Require one exact role."""
    return require_any_role(role)


def require_any_role(*roles: Role) -> Callable[[User], User]:
    """Require any one of the provided roles."""
    allowed_roles = set(roles)

    def dependency(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return dependency


require_admin = require_any_role(*ADMIN_USER_MANAGEMENT_ROLES)
