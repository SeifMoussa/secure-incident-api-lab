# Phase 0 Plan: Secure Incident Management API

## Project Summary

Secure Incident Management API is a portfolio lab for a production-pattern FastAPI backend that manages synthetic security incidents, tickets, evidence notes, remediation tasks, users, roles, and audit logs.

The project is defensive only. It demonstrates secure API design, JWT authentication, RBAC, audit logging, input validation, rate limiting, automated testing, CI, CodeQL, Dependabot, and Agile SDLC documentation.

This is not a deployed production SOC platform and must not be described as production-ready unless limitations are stated clearly. Use production-pattern or production-style language.

## Phase 0 Scope

Phase 0 is planning only. It creates documentation that defines architecture, safety boundaries, data model direction, API groups, testing strategy, threat modeling, and SDLC workflow.

No application source code, endpoints, database models, migrations, git initialization, GitHub publishing, releases, tags, branch protection, GitHub Issues, or GitHub Projects are created in Phase 0.

## In Scope

- Documentation for planned FastAPI architecture.
- Documentation for defensive safety scope.
- Planned authentication and token strategy.
- Planned RBAC roles and permission matrix.
- Planned incident, ticket, evidence note, and remediation workflows.
- Planned audit logging strategy.
- Planned validation, rate limiting, and security headers.
- Planned SQLite development and test database with PostgreSQL-compatible SQLAlchemy models.
- Planned Alembic migration workflow.
- Planned testing strategy with 90% minimum coverage and preference for 95%+.
- Planned STRIDE threat model document.
- Planned GitHub Actions, CodeQL, Dependabot, and release workflow.
- Planned Agile issues and GitHub Projects workflow without creating them.

## Out of Scope

- Offensive security functionality.
- Exploitation, live scanning, packet sniffing, attack automation, or malware behavior.
- Real customer data, real credentials, real tokens, or real evidence files.
- Binary attachment upload or storage.
- Production deployment claims.
- Application implementation during Phase 0.
- GitHub repository publishing or remote configuration during Phase 0.

## Safety Rules

- Use synthetic/demo data only.
- Do not store passwords, access tokens, refresh tokens, or sensitive secrets in logs, audit entries, fixtures, or docs.
- Store refresh tokens hashed when implemented.
- Load JWT secrets from environment/config only.
- Attachments are metadata only.
- Audit middleware must not blindly persist request or response bodies.
- Audit diffing may require service-layer support; do not overpromise perfect automatic diffs from middleware alone.

## Planned Phases

1. Phase 1: Repository scaffold, pyproject, app factory, settings, health endpoint, test skeleton.
2. Phase 2: Database models, SQLAlchemy setup, Alembic baseline.
3. Phase 3: Auth, password policy, JWT, refresh token blocklist.
4. Phase 4: RBAC and user management.
5. Phase 5: Incidents CRUD, filtering, pagination, soft delete.
6. Phase 6: Tickets, evidence notes, remediation tasks.
7. Phase 7: Audit logging and timeline.
8. Phase 8: Security controls: headers, rate limits, CORS, production docs toggle.
9. Phase 9: Validation hardening and security tests.
10. Phase 10: Threat model and API documentation.
11. Phase 11: GitHub Actions, CodeQL, Dependabot.
12. Phase 12: Agile board/issues, release prep, publish, branch protection, v0.1.0 release.

## Phase 0 Quality Check

- Documentation files exist.
- No application source implementation is created.
- No endpoints are implemented.
- No database models are implemented.
- No migrations are created.
- Git is not initialized.
- Nothing is published to GitHub.
- No tags or releases are created.
- No secrets, real credentials, real tokens, real incident data, or real evidence files are included.

## Phase 1 Follow-Up Status

Phase 1 has been started after Phase 0 approval. The scaffold is limited to project tooling, settings, an app factory, `/`, `/health`, and tests. Auth, RBAC, database, migrations, domain workflows, audit logic, CI, git initialization, GitHub publishing, tags, and releases remain out of scope.
