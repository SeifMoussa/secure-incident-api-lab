# Release Preparation

This document prepares the Secure Incident Management API portfolio lab for a future `v0.1.0` GitHub release. It is a local planning artifact only. No tag, release, repository publication, branch protection, live GitHub Issues, or live GitHub Project board has been created yet.

## Project Summary

Production-pattern FastAPI backend for security incident management with JWT auth, RBAC, audit logging, rate limiting, strict validation, threat model, OpenAPI docs, pytest, Ruff, GitHub Actions, CodeQL, and Dependabot.

## Safety Scope

- Defensive project only.
- Synthetic/demo data only.
- No real credentials, real tokens, real customer incident data, or real evidence files.
- Evidence attachments are metadata only.
- No binary upload, file storage, disk file reading for evidence, offensive functionality, exploit code, live scanning, or malware behavior.
- This is not a deployed production SOC platform.

## What v0.1.0 Includes

- FastAPI app factory and settings.
- SQLAlchemy ORM models and Alembic baseline migration.
- JWT authentication, refresh-token blocklist, password policy, and common-password rejection.
- RBAC and ADMIN-only user management.
- Incidents, tickets, evidence notes, metadata-only attachments, and remediation tasks.
- Audit logging, audit read API, and incident timeline.
- Security headers, rate limiting, CORS allowlist, production HTTPS redirect toggle, and production docs disable behavior.
- Validation hardening, safe error handling, and security regression tests.
- STRIDE threat model, API reference, OpenAPI export, CI/CD documentation, and local Agile/release materials.
- GitHub Actions, CodeQL, and Dependabot configuration files.

## Local QA Results

Record final local values before publishing:

- Tests: `python -m pytest`
- Coverage gate: `python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95`
- Ruff: `python -m ruff check .`
- Format: `python -m ruff format --check .`
- Docs safety: `python scripts/check-docs.py`
- OpenAPI export: `python scripts/export_openapi.py`
- Alembic: `python -m alembic upgrade head` and `python -m alembic current`

Latest known pre-publish status from local validation:

- Tests: 248 passed.
- Coverage: 95.60%.
- Coverage gate: 95%.
- Ruff: passed.
- Format check: passed.
- Docs safety: passed.
- OpenAPI export: passed.
- Alembic SQLite upgrade/current: passed.

## Pending Hosted Checks After Push

- Hosted GitHub Actions CI.
- Hosted CodeQL.
- Dependabot alert and update behavior.
- Secret scanning review.
- Code scanning alert review.

## Manual Git Publishing Commands

Run only during the publishing phase:

```bash
git init
git branch -M main
git add .
git commit -m "Release v0.1.0 portfolio lab"
git remote add origin https://github.com/SeifMoussa/secure-incident-api-lab.git
git push -u origin main
```

## GitHub CLI Publishing Commands

Run only during the publishing phase:

```bash
gh repo create SeifMoussa/secure-incident-api-lab --public --source=. --remote=origin --push
```

## Suggested Repository Description

Production-pattern FastAPI backend for security incident management with JWT auth, RBAC, audit logging, rate limiting, strict validation, threat model, OpenAPI docs, pytest, Ruff, GitHub Actions, CodeQL, and Dependabot.

## Suggested GitHub Topics

`fastapi`, `python`, `cybersecurity`, `backend`, `api-security`, `jwt-auth`, `rbac`, `audit-logging`, `incident-management`, `soc`, `blue-team`, `appsec`, `devsecops`, `sqlalchemy`, `alembic`, `pytest`, `ruff`, `codeql`, `github-actions`, `dependabot`, `portfolio`

## Suggested Release

Title: `v0.1.0 - Secure Incident Management API`

Draft notes:

```text
Initial portfolio release of Secure Incident Management API.

Highlights:
- FastAPI backend for synthetic incident management workflows.
- JWT auth, refresh-token blocklist, password policy, and RBAC.
- ADMIN user management, incidents, tickets, evidence notes, metadata-only attachments, and remediation tasks.
- Middleware-driven audit logging, audit read API, and incident timeline.
- Security headers, CORS allowlist, rate limiting, strict validation, and safe validation errors.
- STRIDE threat model, API reference, OpenAPI export, CI, CodeQL, Dependabot, pytest, and Ruff configuration.

Safety:
- Defensive portfolio lab only.
- Synthetic/demo data only.
- No real credentials, real tokens, customer data, or evidence files.
```

## Post-Push Verification Checklist

- [ ] Confirm repository URL: `https://github.com/SeifMoussa/secure-incident-api-lab`
- [ ] Confirm default branch is `main`.
- [ ] Confirm README renders correctly.
- [ ] Confirm `docs/threat_model.md`, `docs/api_reference.md`, and `docs/ci-cd.md` render correctly.
- [ ] Confirm hosted CI starts on push.
- [ ] Confirm hosted CodeQL starts on push or scheduled run.
- [ ] Confirm Dependabot is recognized.

## Code Scanning Checklist

- [ ] Confirm CodeQL workflow is enabled.
- [ ] Review CodeQL results.
- [ ] Triage any findings before release.

## Secret Scanning Checklist

- [ ] Confirm no real credentials, tokens, API keys, database passwords, or secrets are present.
- [ ] Review GitHub secret scanning alerts if available after publishing.

## Dependabot Checklist

- [ ] Confirm pip ecosystem is enabled.
- [ ] Confirm GitHub Actions ecosystem is enabled.
- [ ] Review Dependabot PRs after publishing.

## Branch Protection Checklist

- [ ] Require pull requests before merging.
- [ ] Require hosted CI `Tests`.
- [ ] Require hosted CI `Docs Safety Checks`.
- [ ] Require hosted CI `API Smoke`.
- [ ] Require CodeQL review where practical.
- [ ] Restrict force pushes.

## GitHub Issues Checklist

- [ ] Create planned F1-F14 issues from `docs/agile/backlog.md`.
- [ ] Apply labels.
- [ ] Link issues to project board after board creation.

## GitHub Projects Checklist

- [ ] Create project board.
- [ ] Add columns: Backlog, In Progress, Review, Done.
- [ ] Add planned issues.
- [ ] Capture screenshot after live board exists.

## Screenshot Plan

- Capture README top section.
- Capture API docs locally if needed.
- Capture GitHub Actions summary after hosted CI runs.
- Capture CodeQL status after hosted CodeQL runs.
- Capture project board as `docs/agile/board_sprint1.png` after the live board exists.

Do not add fake screenshots.

## LinkedIn Post Draft

```text
I built Secure Incident Management API, a production-pattern FastAPI portfolio backend for defensive security incident workflows.

It includes JWT auth, RBAC, admin user management, incident/ticket/evidence/remediation workflows, metadata-only attachments, audit logging, rate limiting, security headers, strict validation, a STRIDE threat model, OpenAPI docs, pytest coverage, Ruff, GitHub Actions, CodeQL, and Dependabot configuration.

The project uses synthetic/demo data only and is designed as a defensive backend/security engineering lab.
```

## LinkedIn Projects Section Draft

Secure Incident Management API - Production-pattern FastAPI backend for defensive incident management. Built JWT auth, RBAC, audit logging, incident workflows, metadata-only evidence, security controls, STRIDE threat model, OpenAPI docs, pytest/Ruff quality gates, GitHub Actions, CodeQL, and Dependabot configuration.

## CV Bullets

- Built a production-pattern FastAPI incident management API with JWT auth, RBAC, audit logging, rate limiting, strict validation, and SQLAlchemy ORM.
- Implemented synthetic incident, ticket, evidence note, metadata-only attachment, remediation, audit, and admin user workflows with 95%+ local coverage.
- Added STRIDE threat model, API reference, OpenAPI export, GitHub Actions, CodeQL, Dependabot, and documentation safety checks for a defensive security portfolio project.

## Recruiter-Facing Summary

Secure Incident Management API demonstrates backend engineering and application-security fundamentals in a realistic blue-team workflow: authentication, authorization, secure validation, auditability, security controls, automated testing, and release readiness with no real customer data or offensive functionality.
