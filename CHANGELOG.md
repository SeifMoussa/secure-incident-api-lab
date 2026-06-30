# Changelog

All notable changes to this project will be documented in this file.

This project uses production-pattern language and is a defensive portfolio lab, not a deployed production SOC platform.

## Unreleased

### Added

- Phase 13C annotated `v0.1.0` tag and published GitHub Release.
- Phase 13B live F1-F14 GitHub Issues and backlog labels.
- Phase 13B verified `main` branch protection with strict CI and CodeQL checks, pull-request review, and force-push/deletion restrictions.
- Phase 13B hosted-state documentation for successful CI/CodeQL and zero open code/secret-scanning alerts.
- Phase 13A repository publication and hosted CI investigation.
- Phase 13A correction of CodeQL-reported test calls embedded in assertions.
- Phase 12 recruiter-ready README polish.
- Phase 12 release preparation guide in `RELEASE.md`.
- Phase 12 local Agile planning materials, F1-F14 backlog, board plan, and issue template.
- Phase 12 `CONTRIBUTING.md` with defensive-only contribution policy and quality commands.
- Phase 12 release checklist for local QA and pending hosted/publishing work.
- Phase 12 docs safety updates for release, contributing, Agile, and release-checklist materials.
- Tests for Phase 12 release, Agile, contributing, and docs safety material.
- Phase 7 middleware-driven audit logging for write requests.
- Phase 8 security headers for API responses.
- Phase 10 STRIDE threat model documentation.
- Phase 11 local GitHub Actions CI workflow configuration.
- Phase 11 local CodeQL workflow configuration.
- Phase 11 Dependabot configuration for pip and GitHub Actions.
- Documentation safety script for local and future CI checks.
- Workflow/config tests for CI, CodeQL, Dependabot, and docs safety behavior.
- Phase 10 API reference documentation for implemented endpoints.
- Phase 10 local OpenAPI export script and generated `docs/openapi.json`.
- Documentation safety and endpoint consistency tests.
- Phase 9 validation hardening for client-provided UUID-like IDs.
- Phase 9 safe request validation error handling that does not echo submitted bodies or protected field names.
- Phase 9 security regression tests for mass assignment, sensitive responses, audit redaction, SQLAlchemy ORM/no raw SQL safety, nested-resource access, pagination/filter validation, and OpenAPI security.
- Phase 8 local in-memory rate limiting for login and general endpoints.
- Phase 8 explicit CORS allowlist with local defaults and safe production defaults.
- Phase 8 production-only HTTPS redirect behavior and production docs hardening tests.
- Tests for security headers, rate limiting, CORS, production security config, middleware compatibility, and security-control safety.
- Audit sanitizer for sensitive fields, token-like values, and API-key-like values.
- ADMIN/AUDITOR audit read endpoint with pagination and filters.
- Append-only audit API behavior with no audit mutation routes.
- Incident timeline endpoint backed by sanitized incident audit entries.
- Tests for audit middleware, sanitizer, read filters, append-only behavior, timeline, and safety boundaries.
- Phase 6 nested incident ticket endpoints.
- Phase 6 nested evidence note endpoints with metadata-only attachment support.
- Phase 6 nested remediation task endpoints.
- Completion timestamp behavior for remediation tasks that become `COMPLETE`.
- Tests for tickets, evidence notes, attachment metadata, remediation tasks, RBAC, validation, soft delete, and safety boundaries.
- Phase 5 incident CRUD endpoints.
- Incident schemas with strict validation for title, description, enums, MITRE fields, tags, and assignment.
- Incident service layer using SQLAlchemy ORM only.
- Incident filtering by severity, status, assignee, created date range, and tag.
- Incident pagination using the existing bounded pagination helper.
- Incident soft delete behavior.
- Incident RBAC matrix for ADMIN, ANALYST, VIEWER, and AUDITOR.
- Incident tests for create, list, detail, update, delete, filters, validation, RBAC, and safety boundaries.
- Phase 4 reusable RBAC dependencies for active-user and role checks.
- ADMIN-only user management endpoints for listing users, user detail, role updates, and deactivation.
- Safe admin response schemas that exclude password hashes and token data.
- Pagination helper with bounded page size.
- Admin self-role-change and self-deactivation protections.
- Tests for RBAC behavior, admin user management, deactivation, safety boundaries, and the Phase 4 permissions matrix.
- Phase 3 authentication endpoints: register, login, refresh, logout, and me.
- Password policy with length, uppercase, digit, special character, and common-password checks.
- Bcrypt password hashing through passlib with a bcrypt backend compatible with passlib.
- JWT access and refresh token utilities using HS256 and environment-backed settings.
- Refresh token JTI blocklist behavior backed by the existing token blocklist model.
- Auth request/response schemas that exclude passwords and password hashes from responses.
- Current-user dependency for `/auth/me` only.
- Authentication tests for policy, hashing, JWTs, register/login/refresh/logout/me, and safety boundaries.
- Phase 2 database foundation using SQLAlchemy 2.x style.
- Declarative ORM base, engine helper, session factory helper, and `get_db` dependency placeholder.
- Database-safe enums for roles, incident severity/status, ticket status/priority, remediation status, audit action, and audit outcome.
- ORM models for users, token blocklist, incidents, tickets, evidence notes, evidence attachment metadata, remediation tasks, and audit logs.
- Alembic baseline migration for initial tables.
- In-memory SQLite model test fixtures.
- Model, metadata, enum, Alembic baseline, and route-boundary tests.
- Phase 1 FastAPI scaffold.
- Application factory with development/test docs enabled and production docs disabled.
- Environment-backed settings using pydantic-settings.
- Minimal `/` and `/health` endpoints.
- Phase 1 pytest skeleton and project structure checks.
- Ruff lint and format configuration.
- Local placeholder `.env.example`.
- MIT license.
- Phase 0 planning documentation.
- Architecture plan.
- Security scope.
- Data model plan.
- API plan.
- Testing plan.
- Threat model plan.
- SDLC plan.
- Project completion checklist.
- README draft.

### Not Added

- No binary upload or evidence file storage.
- No live GitHub Project board because the token lacks project scope.
- No Dependabot PR merges.
- No new Phase 9 business/domain workflows.
- No new Phase 10 business/domain workflows.
- No new Phase 11 business/domain workflows.
- No new Phase 12 business/domain workflows.
- No secrets or real incident data.
