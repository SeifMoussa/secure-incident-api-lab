# Changelog

All notable changes to this project will be documented in this file.

This project uses production-pattern language and is a defensive portfolio lab, not a deployed production SOC platform.

## Unreleased

### Added

- Post-release governance: merged release-status documentation and completion comments for F1-F13.
- Annotated `v0.1.0` tag and published GitHub Release.
- Live F1-F14 GitHub Issues and backlog labels.
- Verified `main` branch protection with strict CI and CodeQL checks, pull-request review, and force-push/deletion restrictions.
- Hosted-state documentation for successful CI/CodeQL and zero open code/secret-scanning alerts.
- Repository publication and hosted CI investigation.
- Correction of CodeQL-reported test calls embedded in assertions.
- Recruiter-ready README polish.
- Public v0.1.0 history in `docs/release-notes.md`.
- Local Agile planning materials, F1-F14 backlog, board plan, and issue template.
- `CONTRIBUTING.md` with defensive-only contribution policy and quality commands.
- Release checklist for local QA and pending hosted/publishing work.
- Docs safety updates for release, contributing, Agile, and release-checklist materials.
- Tests for release, Agile, contributing, and docs safety material.
- Middleware-driven audit logging for write requests.
- Security headers for API responses.
- STRIDE threat model documentation.
- Local GitHub Actions CI workflow configuration.
- Local CodeQL workflow configuration.
- Dependabot configuration for pip and GitHub Actions.
- Documentation safety script for local and future CI checks.
- Workflow/config tests for CI, CodeQL, Dependabot, and docs safety behavior.
- API reference documentation for implemented endpoints.
- Local OpenAPI export script and generated `docs/openapi.json`.
- Documentation safety and endpoint consistency tests.
- Validation hardening for client-provided UUID-like IDs.
- Safe request validation error handling that does not echo submitted bodies or protected field names.
- Security regression tests for mass assignment, sensitive responses, audit redaction, SQLAlchemy ORM/no raw SQL safety, nested-resource access, pagination/filter validation, and OpenAPI security.
- Local in-memory rate limiting for login and general endpoints.
- Explicit CORS allowlist with local defaults and safe production defaults.
- Production-only HTTPS redirect behavior and production docs hardening tests.
- Tests for security headers, rate limiting, CORS, production security config, middleware compatibility, and security-control safety.
- Audit sanitizer for sensitive fields, token-like values, and API-key-like values.
- ADMIN/AUDITOR audit read endpoint with pagination and filters.
- Append-only audit API behavior with no audit mutation routes.
- Incident timeline endpoint backed by sanitized incident audit entries.
- Tests for audit middleware, sanitizer, read filters, append-only behavior, timeline, and safety boundaries.
- Nested incident ticket endpoints.
- Nested evidence note endpoints with metadata-only attachment support.
- Nested remediation task endpoints.
- Completion timestamp behavior for remediation tasks that become `COMPLETE`.
- Tests for tickets, evidence notes, attachment metadata, remediation tasks, RBAC, validation, soft delete, and safety boundaries.
- Incident CRUD endpoints.
- Incident schemas with strict validation for title, description, enums, MITRE fields, tags, and assignment.
- Incident service layer using SQLAlchemy ORM only.
- Incident filtering by severity, status, assignee, created date range, and tag.
- Incident pagination using the existing bounded pagination helper.
- Incident soft delete behavior.
- Incident RBAC matrix for ADMIN, ANALYST, VIEWER, and AUDITOR.
- Incident tests for create, list, detail, update, delete, filters, validation, RBAC, and safety boundaries.
- Reusable RBAC dependencies for active-user and role checks.
- ADMIN-only user management endpoints for listing users, user detail, role updates, and deactivation.
- Safe admin response schemas that exclude password hashes and token data.
- Pagination helper with bounded page size.
- Admin self-role-change and self-deactivation protections.
- Tests for RBAC behavior, admin user management, deactivation, safety boundaries, and the admin permissions matrix.
- Authentication endpoints: register, login, refresh, logout, and me.
- Password policy with length, uppercase, digit, special character, and common-password checks.
- Bcrypt password hashing through passlib with a bcrypt backend compatible with passlib.
- JWT access and refresh token utilities using HS256 and environment-backed settings.
- Refresh token JTI blocklist behavior backed by the existing token blocklist model.
- Auth request/response schemas that exclude passwords and password hashes from responses.
- Current-user dependency for `/auth/me` only.
- Authentication tests for policy, hashing, JWTs, register/login/refresh/logout/me, and safety boundaries.
- Database foundation using SQLAlchemy 2.x style.
- Declarative ORM base, engine helper, session factory helper, and `get_db` dependency placeholder.
- Database-safe enums for roles, incident severity/status, ticket status/priority, remediation status, audit action, and audit outcome.
- ORM models for users, token blocklist, incidents, tickets, evidence notes, evidence attachment metadata, remediation tasks, and audit logs.
- Alembic baseline migration for initial tables.
- In-memory SQLite model test fixtures.
- Model, metadata, enum, Alembic baseline, and route-boundary tests.
- FastAPI scaffold.
- Application factory with development/test docs enabled and production docs disabled.
- Environment-backed settings using pydantic-settings.
- Minimal `/` and `/health` endpoints.
- Pytest skeleton and project structure checks.
- Ruff lint and format configuration.
- Local placeholder `.env.example`.
- MIT license.
- Initial planning documentation: architecture plan, security scope, data model plan, API plan, testing plan, threat model plan, SDLC plan, README draft.

### Not Added

- No binary upload or evidence file storage.
- No Dependabot PR merges.
- No new business/domain workflows beyond what's listed above for this release.
- No secrets or real incident data.
