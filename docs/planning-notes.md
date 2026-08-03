# Planning Notes

## Project Summary

Secure Incident Management API is a portfolio lab for a production-pattern FastAPI backend that manages synthetic security incidents, tickets, evidence notes, remediation tasks, users, roles, and audit logs.

The project is defensive only. It demonstrates secure API design, JWT authentication, RBAC, audit logging, input validation, rate limiting, automated testing, CI, CodeQL, Dependabot, and Agile SDLC documentation.

This is not a deployed production SOC platform and must not be described as production-ready unless limitations are stated clearly. Use production-pattern or production-style language.

## Original Planning Scope

Before writing any application code, I planned out the architecture, safety boundaries, data model direction, API groups, testing strategy, threat modeling, and SDLC workflow up front. That upfront planning covered:

- Planned FastAPI architecture.
- Defensive safety scope.
- Authentication and token strategy.
- RBAC roles and permission matrix.
- Incident, ticket, evidence note, and remediation workflows.
- Audit logging strategy.
- Validation, rate limiting, and security headers.
- SQLite development and test database with PostgreSQL-compatible SQLAlchemy models.
- Alembic migration workflow.
- Testing strategy with 90% minimum coverage and preference for 95%+.
- STRIDE threat model document.
- GitHub Actions, CodeQL, Dependabot, and release workflow.
- Agile issues and GitHub Projects workflow.

## Explicitly Out of Scope

- Offensive security functionality.
- Exploitation, live scanning, packet sniffing, attack automation, or malware behavior.
- Real customer data, real credentials, real tokens, or real evidence files.
- Binary attachment upload or storage.
- Production deployment claims.

## Safety Rules

- Use synthetic/demo data only.
- Do not store passwords, access tokens, refresh tokens, or sensitive secrets in logs, audit entries, fixtures, or docs.
- Store refresh tokens hashed where relevant.
- Load JWT secrets from environment/config only.
- Attachments are metadata only.
- Audit middleware must not blindly persist request or response bodies.
- Audit diffing may require service-layer support; do not overpromise perfect automatic diffs from middleware alone.

## Build Order

The build followed this rough sequence, one milestone at a time:

1. Repository scaffold, pyproject, app factory, settings, health endpoint, test skeleton.
2. Database models, SQLAlchemy setup, Alembic baseline.
3. Auth, password policy, JWT, refresh token blocklist.
4. RBAC and user management.
5. Incidents CRUD, filtering, pagination, soft delete.
6. Tickets, evidence notes, remediation tasks.
7. Audit logging and timeline.
8. Security controls: headers, rate limits, CORS, production docs toggle.
9. Validation hardening and security tests.
10. Threat model and API documentation.
11. GitHub Actions, CodeQL, Dependabot.
12. Agile board/issues, release prep, publish, branch protection, v0.1.0 release.

All of the above is implemented; see [`README.md`](../README.md) for current status and [`CHANGELOG.md`](../CHANGELOG.md) for what shipped.
