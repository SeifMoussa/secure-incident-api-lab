# Project Completion Checklist

## Phase 0: Planning

- [x] Create `docs/phase-0-plan.md`.
- [x] Create `docs/architecture.md`.
- [x] Create `docs/security-scope.md`.
- [x] Create `docs/data-model-plan.md`.
- [x] Create `docs/api-plan.md`.
- [x] Create `docs/testing-plan.md`.
- [x] Create `docs/threat-model-plan.md`.
- [x] Create `docs/sdlc-plan.md`.
- [x] Create `PROJECT_COMPLETION_CHECKLIST.md`.
- [x] Create `CHANGELOG.md`.
- [x] Create `README.md` draft.
- [x] Avoid application source code.
- [x] Avoid endpoints.
- [x] Avoid database models.
- [x] Avoid migrations.
- [x] Avoid git initialization.
- [x] Avoid GitHub publishing, tags, releases, issues, projects, and branch protection.

## Phase 1: Repository Scaffold

- [x] Add Python project configuration.
- [x] Create app package.
- [x] Add app factory.
- [x] Add settings module.
- [x] Add health endpoint.
- [x] Add test skeleton.
- [x] Add Ruff configuration.
- [x] Add `.env.example` placeholders.
- [x] Avoid auth, RBAC, database, models, migrations, domain workflows, CI, git, and GitHub publishing.

## Phase 2: Database

- [x] Add SQLAlchemy setup.
- [x] Add planned models.
- [x] Add Alembic baseline.
- [x] Add database tests.
- [x] Add database-safe enums.
- [x] Add in-memory SQLite test fixtures.
- [x] Avoid auth endpoints, JWT encode/decode, RBAC dependencies, service-layer logic, domain API endpoints, audit middleware, CI, git, and GitHub publishing.

## Phase 3: Authentication

- [x] Add registration.
- [x] Add login.
- [x] Add refresh.
- [x] Add logout.
- [x] Add me endpoint.
- [x] Add password policy.
- [x] Add common password rejection.
- [x] Add refresh token blocklist.
- [x] Add password hashing helpers.
- [x] Add JWT access and refresh token utilities.
- [x] Add auth schemas and auth service.
- [x] Add current-user dependency for `/auth/me`.
- [x] Avoid RBAC authorization, admin user management, domain endpoints, audit middleware, rate limiting/security headers, CI, git, and GitHub publishing.

## Phase 4: RBAC and Users

- [x] Add role enforcement.
- [x] Add ADMIN-only user listing.
- [x] Add ADMIN-only user detail.
- [x] Add role change.
- [x] Add deactivation.
- [x] Add reusable RBAC dependencies.
- [x] Add pagination helper.
- [x] Block self-role-change and self-deactivation for admins.
- [x] Verify deactivated users cannot login or use existing access tokens.
- [x] Avoid incident, ticket, evidence, remediation, audit middleware, rate limiting/security headers, CI, git, and GitHub publishing.

## Phase 5: Incidents

- [x] Add incident create/list/detail/update.
- [x] Add soft delete.
- [x] Add filtering and pagination.
- [x] Add incident schemas and validation.
- [x] Add incident RBAC matrix.
- [x] Avoid ticket, evidence, remediation, timeline, audit middleware, rate limiting/security headers, CI, git, and GitHub publishing.

## Phase 6: Tickets, Evidence, Remediation

- [x] Add ticket workflows.
- [x] Add evidence note workflows.
- [x] Add attachment metadata only.
- [x] Add remediation task workflows.
- [x] Add completion timestamp behavior.
- [x] Avoid binary uploads, file reads, file storage, audit middleware, timeline, rate limiting/security headers, CI, git, and GitHub publishing.

## Phase 7: Audit and Timeline

- [x] Add write audit entries.
- [x] Add audit log read endpoints for ADMIN and AUDITOR.
- [x] Add incident timeline.
- [x] Verify sensitive field exclusion.
- [x] Keep audit logs append-only at API level.
- [x] Avoid rate limiting/security headers, CI, git, and GitHub publishing.

## Phase 8: Security Controls

- [x] Add rate limiting.
- [x] Add security headers.
- [x] Add CORS allowlist.
- [x] Add HTTPS redirect production config.
- [x] Add production docs toggle.
- [x] Avoid CI, git, GitHub publishing, tags, releases, and branch protection.

## Phase 9: Validation Hardening

- [x] Harden schemas.
- [x] Add validation tests.
- [x] Add security regression tests.
- [x] Add mass-assignment regression tests.
- [x] Add sensitive response and audit redaction regression tests.
- [x] Add SQLAlchemy ORM/no raw SQL safety checks.
- [x] Add nested-resource, pagination/filter, and OpenAPI security regression tests.
- [x] Avoid new business workflows, CI, git, GitHub publishing, tags, releases, and branch protection.

## Phase 10: Threat Model and API Documentation

- [x] Create `docs/threat_model.md`.
- [x] Complete API documentation.
- [x] Add OpenAPI export support.
- [x] Document limitations.
- [x] Add documentation safety and endpoint consistency tests.
- [x] Avoid new business workflows, CI, git, GitHub publishing, GitHub Issues, GitHub Projects, tags, releases, and branch protection.

## Phase 11: CI, CodeQL, Dependabot

- [x] Add GitHub Actions.
- [x] Add CodeQL.
- [x] Add Dependabot.
- [x] Add docs safety script.
- [x] Add workflow/config tests.
- [x] Verify CI commands locally where possible.
- [x] Document hosted CI/CodeQL as not verified until publishing.
- [x] Avoid git initialization, GitHub publishing, GitHub Issues, GitHub Projects, tags, releases, and branch protection.

## Phase 12: Agile and Release Preparation

- [x] Polish recruiter-ready `README.md`.
- [x] Create `RELEASE.md` release preparation material.
- [x] Create `CONTRIBUTING.md`.
- [x] Create local Agile planning docs and F1-F14 backlog.
- [x] Create local GitHub issue template for future use.
- [x] Create `docs/release-checklist.md`.
- [x] Update docs safety checks for release and Agile materials.
- [x] Avoid application business/domain behavior changes.
- [x] Avoid git initialization, GitHub publishing, hosted verification claims, tags, releases, branch protection, live GitHub Issues, and live GitHub Projects.

## Phase 13: Publishing and Hosted Verification

- [x] Initialize git.
- [x] Publish repository.
- [x] Confirm public repository visibility.
- [x] Verify hosted GitHub Actions.
- [x] Verify hosted CodeQL.
- [x] Confirm zero open code-scanning and secret-scanning alerts.
- [x] Review Dependabot recognition; PRs #1-#4 remain open and unmerged.
- [x] Create planned live GitHub Issues F1-F14.
- [ ] Create planned live GitHub Project.
- [x] Attempt Project creation; token lacks required project scope.
- [x] Configure and verify protected `main` with required checks and pull-request review.
- [ ] Prepare release branch if needed.
- [x] Create annotated `v0.1.0` tag from the verified release-readiness commit.
- [x] Publish the `v0.1.0` GitHub Release.
