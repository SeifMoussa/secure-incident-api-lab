# API Plan

## API Style

The planned API is REST-oriented and grouped by domain. All data is synthetic. Responses must exclude sensitive fields. Authentication uses JWT access tokens and refresh tokens.

No endpoints are implemented in Phase 0.

Phase 1 implements only `GET /` and `GET /health`. Phase 2 adds database models and Alembic migration files only. Phase 3 implements authentication endpoints only: register, login, refresh, logout, and me. Phase 4 implements generic RBAC primitives and ADMIN-only user management. Phase 5 implements incident CRUD, filtering, pagination, soft delete, and incident RBAC. Phase 6 implements nested tickets, evidence notes with metadata-only attachments, and remediation tasks. Phase 7 implements middleware-driven audit logging, ADMIN/AUDITOR audit reads, and incident timeline. Phase 8 implements security headers, rate limiting, CORS allowlist, production-only HTTPS redirect behavior, and production docs disable behavior.
Phase 9 hardens validation and adds security regression tests without adding new endpoints or business workflows.
Phase 10 adds documentation artifacts only: STRIDE threat model, API reference, OpenAPI export, and documentation safety/consistency tests.
Phase 11 adds local CI, CodeQL, Dependabot, and docs safety configuration only. It does not change the API surface.
Phase 12 adds release, Agile, contributing, README polish, and docs safety material only. It does not change the API surface.

## Endpoint Groups

### Health

- `GET /health`

Planned purpose: basic service health for local development and CI smoke checks.

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

Planned controls:

- Password hashing.
- Password policy.
- Common password rejection.
- Access token expiry.
- Refresh token expiry.
- Refresh token blocklist.
- Hashed refresh token storage.

### Users

- `GET /users`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}/role`
- `PATCH /users/{user_id}/deactivate`

Planned controls:

- ADMIN only.
- No password hash or token data in responses.
- Audit entries for role changes and deactivation.

Phase 4 implements these ADMIN-only user management capabilities under `/admin/users`:

- `GET /admin/users/`
- `GET /admin/users/{uid}`
- `PATCH /admin/users/{uid}/role`
- `DELETE /admin/users/{uid}`

Role changes and deactivation create sanitized audit entries through Phase 7 middleware.

### Incidents

- `POST /incidents`
- `GET /incidents`
- `GET /incidents/{incident_id}`
- `PATCH /incidents/{incident_id}`
- `DELETE /incidents/{incident_id}`
- `GET /incidents/{incident_id}/timeline`

Delete is planned as soft delete.

Phase 5 implements incident CRUD under trailing-slash routes:

- `POST /incidents/`
- `GET /incidents/`
- `GET /incidents/{incident_id}`
- `PATCH /incidents/{incident_id}`
- `DELETE /incidents/{incident_id}`

Phase 7 implements `GET /incidents/{incident_id}/timeline` for non-deleted incidents.

### Tickets

- `POST /incidents/{incident_id}/tickets`
- `GET /incidents/{incident_id}/tickets`
- `GET /incidents/{incident_id}/tickets/{ticket_id}`
- `PATCH /incidents/{incident_id}/tickets/{ticket_id}`
- `DELETE /incidents/{incident_id}/tickets/{ticket_id}`

Delete is planned as soft delete.

Phase 6 implements ticket create/list/detail/update/soft-delete nested under incidents.

### Evidence Notes

- `POST /incidents/{incident_id}/evidence`
- `GET /incidents/{incident_id}/evidence`
- `GET /incidents/{incident_id}/evidence/{evidence_id}`
- `PATCH /incidents/{incident_id}/evidence/{evidence_id}`
- `DELETE /incidents/{incident_id}/evidence/{evidence_id}`

Markdown content is allowed. Attachments are metadata only; no binary upload endpoints are planned.

Phase 6 implements evidence note create/list/detail/update/soft-delete. Attachments are metadata only; no binary upload or file storage endpoint exists.

### Remediation Tasks

- `POST /incidents/{incident_id}/remediation`
- `GET /incidents/{incident_id}/remediation`
- `PATCH /incidents/{incident_id}/remediation/{task_id}`
- `DELETE /incidents/{incident_id}/remediation/{task_id}`

When status becomes `COMPLETE`, `completed_at` should be set.

Phase 6 implements remediation create/list/update/soft-delete. `completed_at` is set when status becomes `COMPLETE` and cleared when status changes away from `COMPLETE`.

### Audit Log

- `GET /audit/`

Phase 7 implements paginated audit log reads for ADMIN and AUDITOR. No POST, PATCH, or DELETE endpoints exist for audit logs.

## RBAC Permission Matrix

| Capability | ADMIN | ANALYST | VIEWER | AUDITOR |
| --- | --- | --- | --- | --- |
| Register initial account | Yes | No | No | No |
| Login/refresh/logout/me | Yes | Yes | Yes | Yes |
| List users | Yes | No | No | No |
| View user detail | Yes | No | No | No |
| Change user role | Yes | No | No | No |
| Deactivate user | Yes | No | No | No |
| Create incident | Yes | Yes | No | No |
| List incidents | Yes | Yes | Yes | Yes |
| View incident detail | Yes | Yes | Yes | Yes |
| Update incident | Yes | Yes | No | No |
| Soft delete incident | Yes | No | No | No |
| View incident timeline | Yes | Yes | Yes | Yes |
| Create/update/delete tickets | Yes | Yes | No | No |
| View tickets | Yes | Yes | Yes | Yes |
| Create evidence notes | Yes | Yes | No | No |
| Update evidence notes | Yes | Own only | No | No |
| Delete evidence notes | Yes | No | No | No |
| View evidence notes | Yes | Yes | Yes | Yes |
| Create/update/delete remediation tasks | Yes | Yes | No | No |
| View remediation tasks | Yes | Yes | Yes | Yes |
| Read audit log | Yes | No | No | Yes |

## Validation Strategy

- Use strict Pydantic schemas for request bodies, query parameters, and responses.
- Validate enum-like fields for role, severity, status, and task status.
- Enforce pagination bounds.
- Enforce string length limits.
- Reject unexpected fields where appropriate.
- Sanitize response models by design rather than post-processing raw objects.
- Treat markdown as text content; do not execute or render it server-side.

## Pagination and Filtering

Planned list endpoints should support controlled pagination. Incident lists may support filters by status, severity, owner, created date range, and soft-delete visibility where authorized.

## Response Safety

Responses must exclude:

- Passwords.
- Password hashes.
- Access tokens except token issuance responses.
- Refresh tokens except token issuance responses.
- Token hashes.
- Secret configuration values.
- Sensitive audit-redacted fields.

## Phase 8 Security Controls

Security headers are applied to API responses. Rate limiting protects `/auth/login` and general endpoints using local in-memory counters. CORS uses an explicit allowlist with local development/test defaults and safe empty production defaults unless origins are configured. HTTPS redirect behavior is production-only. API docs are disabled in production settings.

## Phase 9 Validation Hardening

Phase 9 keeps the API surface unchanged. Client-provided UUID-like fields are validated more strictly, validation error responses avoid echoing request bodies, and regression tests cover mass assignment, sensitive responses, audit redaction, nested-resource access, pagination/filter validation, OpenAPI security metadata, and SQLAlchemy ORM/no raw SQL safety.

## Phase 10 Documentation

Phase 10 documents the implemented API surface in `docs/api_reference.md`, creates `docs/threat_model.md`, and exports the current OpenAPI schema to `docs/openapi.json`. Documentation examples use placeholders only and do not introduce new endpoints or workflows.

## Phase 12 Release Documentation

Phase 12 keeps the implemented endpoint set unchanged. It adds recruiter-ready documentation, release preparation material, local Agile planning docs, contributing guidance, and release checklist tracking. Public repository publication is now complete; hosted CI/CodeQL re-verification, live Issues/Projects, branch protection, tags, and releases remain pending.
