# Architecture Plan

## Overview

The planned application is a production-pattern FastAPI service named `app`. It will expose a REST API for managing synthetic security incidents and related workflows. The backend will use SQLAlchemy ORM, Alembic migrations, Pydantic validation, JWT authentication, RBAC authorization, append-only audit logging, and automated tests.

The design favors explicit service-layer behavior for write actions, authorization checks, audit event creation, and validation boundaries.

## Planned Runtime Components

- FastAPI application factory.
- Settings module backed by environment variables.
- SQLAlchemy engine/session management.
- Alembic migration configuration.
- Pydantic request and response schemas.
- Router modules grouped by domain.
- Service modules for business rules and write workflows.
- Repository/data access helpers using SQLAlchemy ORM only.
- Security modules for password hashing, JWTs, refresh token handling, RBAC, rate limiting, and headers.
- Audit service for append-only audit records.
- Test suite using synthetic users and synthetic incident data.

## Planned Directory Structure

```text
secure-incident-api-lab/
  app/
    __init__.py
    main.py
    api/
      deps.py
      router.py
      routes/
        auth.py
        users.py
        incidents.py
        tickets.py
        evidence.py
        remediation.py
        audit.py
        health.py
    core/
      config.py
      security.py
      rate_limit.py
      headers.py
      constants.py
    db/
      base.py
      session.py
      models/
    schemas/
    services/
    repositories/
    audit/
    testsupport/
  alembic/
    versions/
  docs/
  tests/
    unit/
    integration/
    security/
  .github/
    workflows/
  pyproject.toml
  alembic.ini
  README.md
```

Phase 1 creates the initial `app/` package, `app/common/` helpers, `tests/` package, `pyproject.toml`, `.env.example`, `.gitignore`, and `LICENSE`.

Phase 2 creates SQLAlchemy database foundation files, domain model packages, and the Alembic baseline. CI files, routers for auth/domain resources, service-layer workflow modules, audit middleware, git initialization, and GitHub publishing remain planned only.

## Architecture Boundaries

- Routers handle HTTP concerns and dependency injection.
- Services enforce business rules, RBAC decisions, audit event payloads, and workflow transitions.
- Repositories encapsulate ORM queries and persistence.
- Schemas define strict input/output validation and exclude sensitive fields.
- Security utilities handle hashing, token creation, token verification, token revocation, and password policy.
- Audit logging remains append-only and avoids sensitive values.

## Authentication Strategy

- Register, login, refresh, logout, and me endpoints are planned.
- Access tokens use short expiry.
- Refresh tokens use longer expiry and are stored hashed.
- Refresh token blocklist supports logout and token revocation.
- JWT secrets and token settings come from environment-backed configuration.
- Passwords are hashed using a modern password hashing algorithm.
- Password policy rejects weak and common passwords.
- Tokens and password hashes are never returned in API responses.

## RBAC Roles

- ADMIN: Full administrative access.
- ANALYST: Operational incident and workflow management.
- VIEWER: Read-only access to permitted incident workflow data.
- AUDITOR: Read access to audit logs and read-only operational data needed for audit review.

## Audit Logging Strategy

Write actions create audit entries through Phase 7 middleware. The middleware captures request method, path-derived resource context, authenticated actor when available, outcome, client host when available, and sanitized changed-field summaries. Sensitive request/response fields are not stored. Audit diffing remains deliberately conservative because middleware alone cannot reliably produce perfect safe before/after diffs.

Audit entries are append-only. ADMIN and AUDITOR can read audit logs. Audit logs have no PATCH or DELETE endpoints.

## Security Controls

- Local in-memory rate limiting for login and general endpoints.
- Security headers middleware for API responses.
- Strict Pydantic validation.
- SQLAlchemy ORM only; no raw SQL strings.
- Explicit CORS allowlist with local development defaults and safe production defaults.
- HTTPS redirect in production configuration.
- API docs disabled in production configuration.
- Passwords, tokens, secrets, and sensitive fields excluded from responses, logs, and audits.

## Risks and Cautions

- Audit logging must balance traceability with data minimization.
- Diffing must avoid leaking sensitive fields.
- Refresh token replay prevention requires careful hashing, expiry, and revocation design.
- Role checks should be centralized enough to avoid drift but explicit enough to be testable.
- SQLite is suitable for development and tests, but models should remain PostgreSQL-compatible.
- Rate limits must be deterministic in tests.

## Phase 1 Implementation Status

- Implemented app factory: `create_app()`.
- Implemented minimal root endpoint: `GET /`.
- Implemented minimal health endpoint: `GET /health`.
- Implemented settings with pydantic-settings.
- Docs are enabled by default outside production and disabled for production settings.
- Auth, RBAC, database, domain workflows, audit logging, migrations, and CI are not implemented yet.

## Phase 2 Implementation Status

- Implemented SQLAlchemy declarative base.
- Implemented engine and session factory helpers.
- Added `get_db` dependency placeholder for later API phases.
- Implemented ORM models for users, token blocklist, incidents, tickets, evidence notes, evidence attachment metadata, remediation tasks, and audit logs.
- Implemented Alembic baseline migration for the initial tables.
- Domain API endpoints, service-layer domain behavior, audit middleware, rate limiting, security headers, CI, git, and publishing are not implemented yet.

## Phase 3 Implementation Status

- Implemented `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, and `/auth/me`.
- Implemented password policy and common-password rejection.
- Implemented bcrypt password hashing through passlib.
- Implemented JWT access and refresh token utilities.
- Implemented refresh-token JTI blocklist behavior using the token blocklist table.
- Implemented current-user dependency only for `/auth/me`.
- Domain API endpoints, audit middleware, rate limiting/security headers, CI, git, and publishing are not implemented yet.

## Phase 4 Implementation Status

- Implemented reusable RBAC dependencies: current active user, exact-role checks, any-role checks, and ADMIN requirement.
- Authorization uses the current database user state, not only role claims from the access token.
- Implemented ADMIN-only user management routes under `/admin/users`.
- Implemented safe admin schemas that exclude password hashes, passwords, access tokens, refresh tokens, and secrets.
- Implemented bounded pagination helper for admin lists and future list endpoints.
- Implemented self-role-change and self-deactivation protections for admins.
- Ticket, evidence, remediation, audit middleware, audit read routes, rate limiting/security headers, CI, git, and publishing remain unimplemented.

## Phase 5 Implementation Status

- Implemented incident CRUD routes under `/incidents`.
- Implemented incident schemas and static validation for MITRE tactic/technique fields.
- Implemented incident service layer using SQLAlchemy ORM only.
- Implemented filtering by severity, status, assignee, created date range, and tag.
- Implemented pagination with the shared bounded pagination helper.
- Implemented soft delete through `is_deleted=true`.
- Implemented incident RBAC: ADMIN can create/read/update/delete; ANALYST can create/read/update; VIEWER and AUDITOR can read only.
- Ticket, evidence, remediation, incident timeline, audit middleware, audit read routes, rate limiting/security headers, CI, git, and publishing remain unimplemented.

## Phase 6 Implementation Status

- Implemented nested ticket routes under `/incidents/{incident_id}/tickets`.
- Implemented nested evidence note routes under `/incidents/{incident_id}/evidence`.
- Implemented metadata-only evidence attachment records. No binary upload, file reads, or file storage exist.
- Implemented nested remediation task routes under `/incidents/{incident_id}/remediation`.
- Implemented remediation `completed_at` behavior: set when status becomes `COMPLETE`, cleared when status moves away from `COMPLETE`.
- All nested resources are scoped to existing non-deleted incidents.
- Incident timeline, audit middleware, audit read routes, rate limiting/security headers, CI, git, and publishing remain unimplemented until Phase 7 or later.

## Phase 7 Implementation Status

- Implemented middleware-driven audit logging for POST, PATCH, and DELETE write requests.
- Implemented recursive audit sanitization for passwords, password hashes, access tokens, refresh tokens, authorization headers, cookies, API keys, JWT secrets, and secret-like values.
- Implemented safe audit summaries using field names and redaction flags instead of raw request bodies.
- Implemented ADMIN/AUDITOR audit read route under `/audit/` with pagination and filters.
- Implemented append-only audit behavior at the API level; no audit POST, PATCH, or DELETE routes exist.
- Implemented incident timeline under `/incidents/{incident_id}/timeline` using sanitized incident audit entries.
- Rate limiting/security headers, CI, git, and publishing remain unimplemented until Phase 8 or later.

## Phase 8 Implementation Status

- Implemented security headers for API responses, including content type, frame, XSS, referrer, cache-control, CSP, and production HSTS behavior.
- Implemented local in-memory rate limiting for `/auth/login` and general endpoints with settings-controlled limits and test disablement.
- Implemented explicit CORS allowlist behavior without wildcard defaults.
- Implemented production-only HTTPS redirect behavior.
- Hardened production docs disable behavior with tests.
- Verified audit middleware compatibility after security middleware registration.
- CI, git, GitHub publishing, tags, releases, and branch protection remain unimplemented.

## Phase 9 Implementation Status

- Hardened client-provided UUID-like validation for assignment, ownership, and incident filtering fields.
- Added a safe validation error handler that returns generic 422 responses without echoing request bodies or protected field names.
- Added security regression tests for mass assignment, sensitive response safety, audit redaction, SQLAlchemy ORM/no raw SQL safety, nested-resource access, pagination/filter validation, and OpenAPI security metadata.
- No new business/domain workflows were added.
- CI, git, GitHub publishing, tags, releases, and branch protection remain unimplemented.

## Phase 10 Implementation Status

- Added `docs/threat_model.md` with STRIDE analysis, assets, trust boundaries, mitigations, residual risks, and limitations.
- Added `docs/api_reference.md` for implemented endpoints, authentication, RBAC, validation, audit behavior, and safe placeholder-only examples.
- Added `scripts/export_openapi.py` and generated `docs/openapi.json` without requiring a running server or network calls.
- Added documentation safety, OpenAPI export, and endpoint consistency tests.
- No new business/domain workflows were added.
- CI, git, GitHub publishing, GitHub Issues, GitHub Projects, tags, releases, and branch protection remain unimplemented.

## Phase 11 Implementation Status

- Added local GitHub Actions CI configuration with Tests, Docs Safety Checks, and API Smoke jobs.
- Added local CodeQL configuration for Python with security-and-quality queries.
- Added Dependabot configuration for pip and GitHub Actions.
- Added `scripts/check-docs.py` for documentation safety checks.
- Added `docs/ci-cd.md` documenting local configuration and hosted verification limitations.
- Hosted GitHub CI and CodeQL are not verified yet because the repository is not published.
- Git initialization, GitHub publishing, GitHub Issues, GitHub Projects, tags, releases, and branch protection remain unimplemented.

## Phase 12 Implementation Status

- Polished `README.md` for recruiter review while preserving production-pattern portfolio wording.
- Added `RELEASE.md`, `CONTRIBUTING.md`, and `docs/release-checklist.md`.
- Added local Agile planning docs under `docs/agile/` and a local issue template for future GitHub Issues.
- Expanded documentation safety checks and tests for release, contributing, Agile, and release checklist materials.
- No application runtime architecture, API behavior, database schema, or business/domain workflow changed.
- Git initialization, GitHub publishing, hosted CI/CodeQL verification, live GitHub Issues, live GitHub Projects, tags, releases, and branch protection remain unimplemented.
