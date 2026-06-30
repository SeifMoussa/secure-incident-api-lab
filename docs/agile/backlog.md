# Planned Backlog

The following backlog is the source of truth for the live F1-F14 GitHub Issues created in Phase 13B. The issues remain open pending Project organization and release governance.

## F1: Project Scaffold and Health API

Labels: `docs`, `test`

Scope: Create the FastAPI app factory, settings, project structure, root endpoint, health endpoint, Ruff setup, and baseline tests.

Acceptance criteria:

- App factory creates the API consistently.
- `/` and `/health` return safe responses.
- Production docs behavior is configurable.
- Synthetic/demo safety wording exists.

Status: Implemented locally and verified before publishing.

## F2: Database Foundation

Labels: `incident`, `ticket`, `evidence`, `remediation`, `audit`, `test`

Scope: Add SQLAlchemy ORM foundation, domain models, enums, token blocklist model, audit log model, and Alembic baseline.

Acceptance criteria:

- ORM tables are represented with SQLAlchemy patterns.
- Alembic baseline exists.
- Evidence attachment records are metadata only.
- Tests verify models and migration metadata.

Status: Implemented locally and verified before publishing.

## F3: Authentication

Labels: `auth`, `security`, `test`

Scope: Implement register, login, refresh, logout, `/auth/me`, password policy, password hashing, JWT helpers, and refresh-token blocklist.

Acceptance criteria:

- Password policy rejects weak synthetic inputs.
- Access and refresh tokens are typed.
- Logout blocks refresh-token JTI values.
- Responses never expose password hashes.

Status: Implemented locally and verified before publishing.

## F4: RBAC and Admin User Management

Labels: `rbac`, `security`, `test`

Scope: Add ADMIN, ANALYST, VIEWER, and AUDITOR role checks plus ADMIN-only user listing, detail, role update, and deactivation.

Acceptance criteria:

- Admin endpoints require ADMIN.
- Current database role state controls authorization.
- Self role-change and self-deactivation protections exist.
- Admin responses exclude secrets and password hashes.

Status: Implemented locally and verified before publishing.

## F5: Incident CRUD

Labels: `incident`, `validation`, `test`

Scope: Add incident create, list, detail, update, soft delete, filtering, pagination, validation, and RBAC.

Acceptance criteria:

- Incidents are synthetic/demo records only.
- Server-managed fields are rejected.
- Pagination and filters are bounded and validated.
- Soft-deleted incidents are hidden from normal reads.

Status: Implemented locally and verified before publishing.

## F6: Tickets, Evidence, and Remediation

Labels: `ticket`, `evidence`, `remediation`, `test`

Scope: Add nested ticket, evidence note, metadata-only attachment, and remediation task workflows.

Acceptance criteria:

- Nested resources are scoped to non-deleted parent incidents.
- Evidence attachments remain metadata only.
- No binary upload, file storage, or disk file reading exists.
- Remediation completion timestamps are controlled by the server.

Status: Implemented locally and verified before publishing.

## F7: Audit Logging and Timeline

Labels: `audit`, `security`, `test`

Scope: Add middleware-driven audit logging, sanitized audit read API, and incident timeline.

Acceptance criteria:

- POST, PATCH, and DELETE requests create audit entries.
- ADMIN and AUDITOR can read audit logs.
- Audit API is append-only.
- Sensitive fields are redacted from audit entries.

Status: Implemented locally and verified before publishing.

## F8: Security Controls

Labels: `security`, `test`

Scope: Add security headers, rate limiting, CORS allowlist, production HTTPS redirect behavior, and production docs hardening.

Acceptance criteria:

- Security headers appear on normal and practical error responses.
- Login and general rate limits are configurable.
- CORS does not use wildcard defaults.
- Production docs are disabled.

Status: Implemented locally and verified before publishing.

## F9: Validation Hardening and Security Regression Tests

Labels: `validation`, `security`, `test`

Scope: Harden schemas and add regression tests for mass assignment, sensitive responses, audit redaction, SQLAlchemy ORM usage, nested resources, pagination, and OpenAPI security.

Acceptance criteria:

- Server-managed fields are rejected or safely ignored only where documented.
- Error responses avoid stack traces and internal details.
- SQLAlchemy ORM/query-builder patterns are used.
- Security regression tests are meaningful.

Status: Implemented locally and verified before publishing.

## F10: Threat Model and API Reference

Labels: `docs`, `security`, `test`

Scope: Add STRIDE threat model, API reference, OpenAPI export, documentation safety tests, and endpoint consistency tests.

Acceptance criteria:

- STRIDE categories, assets, trust boundaries, mitigations, residual risks, and limitations are documented.
- API reference covers implemented endpoints.
- Examples use placeholders only.
- OpenAPI export works without a running server.

Status: Implemented locally and verified before publishing.

## F11: CI, CodeQL, Dependabot, and Docs Safety

Labels: `ci`, `security`, `docs`, `test`

Scope: Add local GitHub Actions CI, CodeQL workflow, Dependabot configuration, docs safety script, workflow tests, and CI/CD documentation.

Acceptance criteria:

- CI has Tests, Docs Safety Checks, and API Smoke jobs.
- Coverage gate is 95%.
- CodeQL is configured for Python.
- Dependabot covers pip and GitHub Actions.

Status: Implemented locally and verified before publishing.

## F12: Agile and Release Preparation

Labels: `release`, `docs`, `ci`

Scope: Add recruiter-ready README polish, release preparation material, local Agile backlog, issue template, contributing guide, release checklist, docs safety updates, and final local QA.

Acceptance criteria:

- README is recruiter-ready and avoids production-readiness overclaims.
- Release material includes pending hosted checks and publishing checklist.
- Agile materials are local only.
- Final local QA commands pass.

Status: Implemented locally and verified before publishing.

## F13: Repository Publishing

Labels: `release`, `ci`

Scope: Initialize git, publish the repository, verify hosted CI and CodeQL, review Dependabot recognition, and keep release/tag creation separate until checks pass.

Acceptance criteria:

- Repository is published at the planned URL.
- Hosted GitHub Actions and CodeQL status are reviewed.
- No real credentials, tokens, or customer data are present.
- Publishing evidence is documented.

Status: Publishing and hosted verification completed in Phase 13A. Release/tag/branch protection remain separate until Phase 13B/13C.

## F14: Release, Branch Protection, Issues, and Project Board

Labels: `release`, `ci`, `docs`

Scope: Create live GitHub Issues, create the GitHub Project board, configure branch protection, create `v0.1.0` tag/release, and capture real screenshots after hosted setup exists.

Acceptance criteria:

- Live issues match the planned backlog.
- Project board columns are Backlog, In Progress, Review, and Done.
- Branch protection requires appropriate checks.
- Release notes match the release draft after hosted checks are verified.

Status: Pending release governance, branch protection, tag/release, and final screenshots.
