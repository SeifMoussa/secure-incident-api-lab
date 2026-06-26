"""Middleware-driven audit logging for write requests."""

import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.context import clear_audit_context, get_audit_context
from app.audit.sanitizer import safe_field_summary
from app.audit.service import create_audit_entry
from app.auth.models import User
from app.auth.utils import ACCESS_TOKEN_TYPE, TokenError, decode_token
from app.common.enums import AuditAction, AuditOutcome
from app.config import Settings
from app.database import SessionLocal, get_db

WRITE_METHODS = {"POST", "PATCH", "DELETE"}
SKIPPED_WRITE_PATHS = {"/auth/refresh"}


class AuditMiddleware:
    """Create sanitized audit entries for write requests."""

    def __init__(self, app: Callable[..., Any]) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"].upper()
        path = scope["path"]
        should_audit = method in WRITE_METHODS and path not in SKIPPED_WRITE_PATHS
        if not should_audit:
            await self.app(scope, receive, send)
            return

        clear_audit_context()
        body = await self._read_body(receive)
        status_code = 500
        response_chunks: list[bytes] = []

        async def replay_receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body, "more_body": False}

        async def capture_send(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            elif message["type"] == "http.response.body":
                response_chunks.append(message.get("body", b""))
            await send(message)

        try:
            await self.app(scope, replay_receive, capture_send)
        finally:
            self._write_audit_entry(
                scope=scope,
                method=method,
                path=path,
                request_body=body,
                response_body=b"".join(response_chunks),
                status_code=status_code,
            )
            clear_audit_context()

    async def _read_body(self, receive: Callable) -> bytes:
        chunks: list[bytes] = []
        more_body = True
        while more_body:
            message = await receive()
            chunks.append(message.get("body", b""))
            more_body = message.get("more_body", False)
        return b"".join(chunks)

    def _write_audit_entry(
        self,
        *,
        scope: dict[str, Any],
        method: str,
        path: str,
        request_body: bytes,
        response_body: bytes,
        status_code: int,
    ) -> None:
        audit_target = _resolve_audit_target(method, path)
        if audit_target is None:
            return

        request_json = _parse_json(request_body)
        response_json = _parse_json(response_body)
        db, close_db = _open_audit_session(scope)
        try:
            app_settings: Settings = scope["app"].state.settings
            context = get_audit_context()
            action = context.action if context and context.action else audit_target["action"]
            resource_type = audit_target["resource_type"]
            if context and context.resource_type:
                resource_type = context.resource_type
            resource_id = (
                context.resource_id
                if context and context.resource_id
                else _resolve_resource_id(audit_target, response_json)
            )
            changes = (
                {"fields_changed": sorted(context.changed_fields)}
                if context and context.changed_fields
                else safe_field_summary(request_json)
            )
            actor_id = _resolve_actor_id(
                db,
                settings=app_settings,
                scope=scope,
                request_json=request_json,
                status_code=status_code,
                action=action,
            )
            create_audit_entry(
                db,
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=_client_host(scope),
                changes=changes,
                outcome=AuditOutcome.SUCCESS if status_code < 400 else AuditOutcome.FAILURE,
            )
        finally:
            close_db()


def _resolve_audit_target(method: str, path: str) -> dict[str, Any] | None:
    segments = [segment for segment in path.strip("/").split("/") if segment]
    if segments[:2] == ["auth", "login"]:
        return {"action": AuditAction.LOGIN, "resource_type": "auth", "resource_id": None}
    if segments[:2] == ["auth", "logout"]:
        return {"action": AuditAction.LOGOUT, "resource_type": "auth", "resource_id": None}
    if segments[:2] == ["auth", "register"]:
        return {"action": AuditAction.CREATE, "resource_type": "auth", "resource_id": None}
    if len(segments) >= 2 and segments[:2] == ["admin", "users"]:
        action = AuditAction.DELETE if method == "DELETE" else AuditAction.UPDATE
        return {
            "action": action,
            "resource_type": "user",
            "resource_id": segments[2] if len(segments) > 2 else None,
        }
    if not segments or segments[0] != "incidents":
        return None
    if len(segments) == 1:
        return {"action": AuditAction.CREATE, "resource_type": "incident", "resource_id": None}
    if len(segments) == 2:
        action = AuditAction.DELETE if method == "DELETE" else AuditAction.UPDATE
        return {"action": action, "resource_type": "incident", "resource_id": segments[1]}
    if len(segments) >= 3 and segments[2] in {"tickets", "evidence", "remediation"}:
        resource_type = {
            "tickets": "ticket",
            "evidence": "evidence",
            "remediation": "remediation",
        }[segments[2]]
        action = _action_from_method(method)
        resource_id = segments[3] if len(segments) > 3 else None
        return {"action": action, "resource_type": resource_type, "resource_id": resource_id}
    return None


def _action_from_method(method: str) -> AuditAction:
    if method == "PATCH":
        return AuditAction.UPDATE
    if method == "DELETE":
        return AuditAction.DELETE
    return AuditAction.CREATE


def _parse_json(body: bytes) -> Any:
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _resolve_resource_id(audit_target: dict[str, Any], response_json: Any) -> str | None:
    if audit_target["resource_id"] is not None:
        return audit_target["resource_id"]
    if not isinstance(response_json, dict):
        return None
    resource_type = audit_target["resource_type"]
    keys = {
        "incident": "incident_id",
        "ticket": "ticket_id",
        "evidence": "evidence_id",
        "remediation": "task_id",
        "user": "user_id",
    }
    key = keys.get(resource_type)
    if key is None:
        return None
    if isinstance(response_json.get(key), str):
        return response_json[key]
    for value in response_json.values():
        if isinstance(value, dict) and isinstance(value.get(key), str):
            return value[key]
    return None


def _resolve_actor_id(
    db: Session,
    *,
    settings: Settings,
    scope: dict[str, Any],
    request_json: Any,
    status_code: int,
    action: AuditAction,
) -> str | None:
    token_user_id = _actor_from_authorization_header(settings, scope)
    if token_user_id is not None:
        return token_user_id
    if status_code >= 400 or action not in {AuditAction.LOGIN, AuditAction.CREATE}:
        return None
    if isinstance(request_json, dict) and isinstance(request_json.get("email"), str):
        user = db.scalar(select(User).where(User.email == request_json["email"].lower()))
        return user.user_id if user is not None else None
    return None


def _actor_from_authorization_header(settings: Settings, scope: dict[str, Any]) -> str | None:
    for key, value in scope.get("headers", []):
        if key.lower() == b"authorization":
            header_value = value.decode("latin1")
            if not header_value.lower().startswith("bearer "):
                return None
            try:
                payload = decode_token(
                    settings,
                    header_value.split(" ", 1)[1],
                    expected_type=ACCESS_TOKEN_TYPE,
                )
            except TokenError:
                return None
            return payload["sub"]
    return None


def _open_audit_session(scope: dict[str, Any]) -> tuple[Session, Callable[[], None]]:
    override = scope["app"].dependency_overrides.get(get_db)
    if override is None:
        db = SessionLocal()
        return db, db.close

    db_source = override()
    if hasattr(db_source, "__next__"):
        db = next(db_source)

        def close_override() -> None:
            try:
                next(db_source)
            except StopIteration:
                return

        return db, close_override
    return db_source, lambda: None


def _client_host(scope: dict[str, Any]) -> str | None:
    client = scope.get("client")
    if client is None:
        return None
    return str(client[0])
