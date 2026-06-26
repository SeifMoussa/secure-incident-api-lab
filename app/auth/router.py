"""Authentication API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import (
    AccessTokenResponse,
    AuthMessageResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.auth.service import (
    AuthServiceError,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    user_profile,
)
from app.config import Settings, get_settings
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]
) -> UserProfileResponse:
    try:
        return register_user(db, payload)
    except AuthServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    try:
        return login_user(db, settings, payload)
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        ) from exc


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AccessTokenResponse:
    try:
        return refresh_access_token(db, settings, payload)
    except AuthServiceError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", response_model=AuthMessageResponse)
def logout(
    payload: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthMessageResponse:
    return logout_user(db, settings, payload.refresh_token)


@router.get("/me", response_model=UserProfileResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserProfileResponse:
    return user_profile(current_user)
