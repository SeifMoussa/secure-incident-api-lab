# Secure Incident Management API

Production-pattern FastAPI backend for defensive security incident management.

This is a defensive portfolio lab, not a deployed production SOC platform. It uses synthetic/demo data only. Do not use real credentials, real tokens, real customer incident data, or real evidence files.

## What This Demonstrates

Secure Incident Management API demonstrates backend and application-security engineering patterns for a security operations workflow:

- FastAPI application factory.
- SQLAlchemy ORM models and Alembic baseline migrations.
- JWT authentication with access and refresh tokens.
- Refresh-token JTI blocklist.
- Password hashing, password policy, and common-password rejection.
- RBAC for ADMIN, ANALYST, VIEWER, and AUDITOR roles.
- ADMIN-only user management.
- Incident CRUD, filtering, pagination, and soft delete.
- Nested tickets, evidence notes, metadata-only attachments, and remediation tasks.
- Middleware-driven audit logging and incident timeline.
- Rate limiting, security headers, CORS allowlist, and production docs toggle.
- Strict validation, mass-assignment protection, and safe validation errors.
- STRIDE threat model and API reference.
- OpenAPI export.
- Pytest coverage, Ruff lint/format checks, GitHub Actions configuration, CodeQL configuration, and Dependabot configuration.

## Target Roles

This project is designed to be relevant for:

- Backend Developer.
- Junior Security Engineer.
- SOC Automation Analyst.
- Blue Team Analyst.
- Application Security trainee.
- DevSecOps trainee.

## Feature Summary

Implemented endpoint groups:

- General: `/`, `/health`
- Authentication: `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`
- Admin users: `/admin/users/`, `/admin/users/{uid}`, `/admin/users/{uid}/role`
- Incidents: `/incidents/`, `/incidents/{incident_id}`, `/incidents/{incident_id}/timeline`
- Tickets: `/incidents/{incident_id}/tickets/`
- Evidence notes: `/incidents/{incident_id}/evidence/`
- Remediation tasks: `/incidents/{incident_id}/remediation/`
- Audit reads: `/audit/`

Evidence attachments are metadata only. There is no binary upload, no file storage, and no disk file reading for evidence.

## Architecture Overview

```text
app/
  admin/          ADMIN-only user management
  audit/          audit middleware, sanitizer, schemas, read API
  auth/           registration, login, refresh, logout, JWT helpers
  common/         shared enums, pagination, dependencies, validation, errors
  evidence/       evidence notes and metadata-only attachment workflows
  incidents/      incident CRUD and timeline
  remediation/    remediation task workflows
  security/       headers, CORS, rate limiting, middleware registration
  tickets/        ticket workflows
alembic/          baseline migration
docs/             security, API, testing, Agile, CI/CD, release docs
tests/            unit, integration, security, docs, workflow tests
```

The application uses strict Pydantic schemas at the API boundary, service-layer business rules, SQLAlchemy ORM/query-builder patterns, and local SQLite for development and tests.

## Security Model

- JWT bearer authentication protects operational endpoints.
- Refresh tokens are typed and blocklisted by JTI on logout.
- Current database user state is used for authorization so deactivation and role changes take effect.
- RBAC gates ADMIN, ANALYST, VIEWER, and AUDITOR capabilities.
- Write requests are audit-logged by middleware with sanitized metadata.
- Sensitive fields are excluded or redacted from responses, validation errors, audit logs, docs, and tests.
- CORS defaults to an explicit local allowlist and safe production empty allowlist.
- Security headers are applied to API responses.
- Rate limiting protects login and general endpoints in normal configuration.
- Production settings disable interactive API docs and reject placeholder JWT secrets.

## RBAC Matrix

| Capability | ADMIN | ANALYST | VIEWER | AUDITOR |
| --- | --- | --- | --- | --- |
| Login/refresh/logout/me | Yes | Yes | Yes | Yes |
| List/view users | Yes | No | No | No |
| Change user role | Yes | No | No | No |
| Deactivate user | Yes | No | No | No |
| Create incidents | Yes | Yes | No | No |
| Read incidents | Yes | Yes | Yes | Yes |
| Update incidents | Yes | Yes | No | No |
| Soft-delete incidents | Yes | No | No | No |
| View incident timeline | Yes | Yes | Yes | Yes |
| Create/update/delete tickets | Yes | Yes | No | No |
| Read tickets | Yes | Yes | Yes | Yes |
| Create evidence notes | Yes | Yes | No | No |
| Update evidence notes | Yes | Own only | No | No |
| Delete evidence notes | Yes | No | No | No |
| Read evidence notes | Yes | Yes | Yes | Yes |
| Create/update/delete remediation tasks | Yes | Yes | No | No |
| Read remediation tasks | Yes | Yes | Yes | Yes |
| Read audit logs | Yes | No | No | Yes |

## Audit Logging

Audit logging is middleware-driven for write requests. It records safe metadata such as actor, action, resource type, resource ID, timestamp, client host where available, outcome, and sanitized change summaries.

Audit logs never intentionally store passwords, password hashes, access tokens, refresh tokens, authorization headers, API keys, JWT secrets, cookies, raw tokens, or secret-looking values. Audit read access is ADMIN/AUDITOR only. No audit mutation routes exist.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Use placeholder-only local settings. Do not put real secrets in `.env`.

```bash
copy .env.example .env
```

## Local Quality Commands

```bash
python scripts/export_openapi.py
python scripts/check-docs.py
python -m py_compile scripts/export_openapi.py scripts/check-docs.py
python -m pytest
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95
python -m ruff check .
python -m ruff format --check .
python -m uvicorn app.main:create_app --factory --help
python -m alembic upgrade head
python -m alembic current
```

## Current Quality Status

Latest local Phase 13A audit validation:

- Tests: 244 passed after removing four stale/redundant phase-boundary tests.
- Coverage: 95.60%.
- Coverage gate: 95%.
- Ruff: passed.
- Format check: passed.
- Docs safety: passed.
- OpenAPI export: passed.
- Alembic SQLite upgrade/current: passed.

The repository has been published at `https://github.com/SeifMoussa/secure-incident-api-lab`. The latest hosted CI run completed its Docs Safety Checks and API Smoke jobs successfully, but its Tests job failed on stale route-inspection tests. Hosted CI has not passed after the local audit fixes yet.

The repository is published publicly. Code scanning is available, and real test-side-effect findings were corrected locally. Hosted CI and hosted CodeQL verification are pending until the next pushed run completes; neither is claimed to have passed after the audit fixes.

## Documentation

- [STRIDE threat model](docs/threat_model.md)
- [API reference](docs/api_reference.md)
- [OpenAPI JSON](docs/openapi.json)
- [CI/CD configuration](docs/ci-cd.md)
- [Release checklist](docs/release-checklist.md)
- [Agile planning docs](docs/agile/README.md)
- [Security scope](docs/security-scope.md)
- [Testing plan](docs/testing-plan.md)

## Limitations

- This is a portfolio lab, not a deployed production SOC platform.
- No real production deployment, monitoring, backup, disaster recovery, or compliance review is included.
- Local SQLite is used for development and tests.
- In-memory rate limiting is not distributed.
- Audit logs are append-only through the API, but no external immutable audit store is implemented.
- Hosted CI re-verification remains pending after the local audit fixes.
- CodeQL remains configured and is expected to run for the public repository after the next authorized push.
- Branch protection, tags, releases, live Issues, and a live Project board have not been created.

## Roadmap

- Phase 12: local Agile and release preparation materials complete.
- Phase 13A: repository publication complete; local audit fixes and hosted CI re-verification pending.
- Phase 13B: not started. Live Issues/Project, branch protection, tag, and release work remain pending.

## License

MIT. See [LICENSE](LICENSE).
