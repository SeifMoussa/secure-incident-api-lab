# Testing Plan

## Coverage Target

The minimum planned test coverage is 90%. The preferred target is 95% or higher.

Coverage should be meaningful rather than line-count only. Security behavior, authorization boundaries, validation failures, and audit behavior are high priority.

## Test Data Rules

- Use synthetic users only.
- Use synthetic incidents only.
- Use synthetic tickets, evidence notes, and remediation tasks only.
- Do not use real passwords, real tokens, real credentials, real incident data, or real evidence files.
- Fixtures must avoid values that look like real secrets.

## Planned Test Areas

- Authentication.
- Password policy.
- Common password rejection.
- JWT expiry behavior.
- Refresh token expiry.
- Refresh token blocklist.
- Logout behavior.
- RBAC permissions.
- User management authorization.
- Incident CRUD.
- Ticket workflows.
- Evidence notes and metadata-only attachments.
- Remediation task completion timestamp behavior.
- Audit entry creation for write actions.
- Audit log read permissions.
- Sensitive field exclusion.
- Security headers.
- Rate limiting.
- CORS configuration.
- Production docs toggle.
- Validation failures.
- Pagination and filtering.
- Soft delete behavior.

## Phase 1 Tests

Phase 1 adds tests for:

- App factory creation.
- Health endpoint status and response shape.
- Root endpoint safe message.
- Development/test docs enabled.
- Production docs disabled.
- Settings safe defaults.
- Production secret validation guard.
- Placeholder-only `.env.example`.
- Required Phase 1 files.
- Absence of auth, RBAC, database, migrations, domain workflow, audit, and CI implementation.

## Phase 2 Tests

Phase 2 adds tests for:

- In-memory SQLite table creation.
- Expected table names.
- SQLAlchemy engine/session helpers.
- User model fields and email uniqueness metadata.
- Role enum values.
- Incident model fields, enum values, JSON tags, timestamps, and soft delete field.
- Ticket model fields, enum values, relationship, and soft delete field.
- Evidence note model fields, JSON tags, and metadata-only attachment records.
- Remediation task fields, enum values, relationship, completion fields, and soft delete field.
- Audit log fields, enum values, JSON-compatible changes, and absence of update/delete route behavior.
- Token blocklist fields and unique JTI metadata.
- Alembic env and baseline migration files.
- Absence of auth/domain API routes and CI files.

## Phase 3 Tests

Phase 3 adds tests for:

- Password policy failures and valid synthetic test passwords.
- Bcrypt password hashing and verification.
- JWT access/refresh token claims, type validation, expiry rejection, and missing-secret behavior.
- Registration success, duplicate email rejection, invalid email rejection, and common-password rejection.
- Password hash storage without raw password storage.
- Login success, generic wrong-password failure, and inactive-user rejection.
- Refresh success and refresh-token type validation.
- Logout JTI blocklisting and refresh rejection after logout.
- `/auth/me` success, missing token rejection, and refresh-token rejection.
- Response body safety for passwords, password hashes, and JWT secrets.
- Continued absence of RBAC, admin, domain, CI, git, and publishing work.

## Phase 4 Tests

Phase 4 adds tests for:

- `require_admin` allowing ADMIN and blocking ANALYST, VIEWER, and AUDITOR.
- Missing, invalid, expired, wrong-type, and inactive-user token failures.
- Authorization using current database role instead of stale token role claims.
- ADMIN-only user list and detail endpoints.
- Safe admin responses without password hashes, token values, or secrets.
- Role updates with enum validation and non-admin rejection.
- Admin self-role-change protection.
- Soft deactivation with non-admin rejection and admin self-deactivation protection.
- Deactivated users being unable to login or use existing access tokens.
- Pagination defaults and maximum page size enforcement.
- Continued absence of incident, ticket, evidence, remediation, audit middleware, rate limiting/security headers, CI, git, and publishing work.

## Phase 5 Tests

Phase 5 adds tests for:

- ADMIN and ANALYST incident creation.
- VIEWER and AUDITOR create/update/delete rejection where applicable.
- Missing, invalid, and inactive-user authentication rejection.
- Managed fields such as `created_by`, `created_at`, and `is_deleted` rejected from create/update requests.
- Assignee validation for active existing users.
- Incident list and detail access for all roles.
- Filtering by severity, status, assigned user, created date range, and tag.
- Pagination defaults and maximum page size enforcement.
- Detail 404 behavior for missing and soft-deleted incidents.
- ADMIN and ANALYST update behavior.
- ADMIN-only soft delete.
- Soft-deleted incidents excluded from lists and details.
- Response safety for password hashes, passwords, tokens, and secrets.
- Continued absence of ticket, evidence, remediation, audit middleware, rate limiting/security headers, CI, git, and publishing work.

## Phase 6 Tests

Phase 6 adds tests for:

- Ticket create/list/detail/update/soft-delete paths.
- Ticket RBAC, validation, active assignee checks, parent incident scoping, and soft-delete exclusion.
- Evidence note create/list/detail/update/soft-delete paths.
- Evidence RBAC, analyst own-note update rule, ADMIN-only delete, validation, parent incident scoping, and soft-delete exclusion.
- Evidence attachment metadata acceptance and rejection of unsafe filename/path-like metadata.
- Remediation create/list/update/soft-delete paths.
- Remediation RBAC, active owner checks, validation, parent incident scoping, soft-delete exclusion, and completion timestamp transitions.
- Response safety for passwords, password hashes, access tokens, refresh tokens, authorization headers, API keys, and secrets.
- Continued absence of audit middleware, incident timeline, rate limiting/security headers, CI, git, and publishing work.

## Phase 7 Tests

Phase 7 adds tests for:

- Audit sanitizer redaction for passwords, password hashes, access tokens, refresh tokens, authorization headers, API keys, JWT secrets, cookies, token-like/API-key-like strings, and nested sensitive values.
- Middleware audit creation for register, login, logout, incident writes, ticket writes, evidence writes, remediation writes, and failed unauthorized writes.
- Audit outcome behavior for successful and failed write requests.
- Actor attribution for authenticated writes and safe null actor behavior for unauthenticated failures.
- ADMIN/AUDITOR audit read access and ANALYST/VIEWER denial.
- Audit filters for resource type, resource ID, actor, action, and outcome.
- Audit pagination and newest-first ordering.
- Append-only API behavior with no audit POST, PATCH, or DELETE routes.
- Incident timeline access for all incident-read roles, oldest-first ordering, and 404 behavior for missing or soft-deleted incidents.
- Audit and timeline response safety for passwords, password hashes, token values, authorization headers, API keys, and secrets.
- Continued absence of rate limiting/security headers, CI, git, and publishing work.

## Phase 8 Tests

Phase 8 adds tests for:

- Security headers on normal, auth, unauthorized, forbidden, and production responses.
- Docs remaining usable in development/test and disabled in production.
- Login and general endpoint rate limiting with low deterministic test limits.
- Rate limiting disablement for normal test workflows.
- Safe 429 responses without passwords, tokens, authorization headers, API keys, or secrets.
- CORS allowed-origin and disallowed-origin behavior without wildcard defaults.
- Production CORS safe defaults and explicit production allowlist behavior.
- Production-only HTTPS redirect behavior.
- Middleware compatibility for auth, admin, incidents, nested resources, audit logging, and incident timeline.
- Continued absence of CI, git, publishing, tags, releases, and branch protection work.

## Phase 9 Tests

Phase 9 adds tests for:

- Validation hardening for MITRE fields, tags, evidence attachment metadata, pagination, enum filters, UUID-like filters, and datetime filters.
- Mass-assignment rejection for registration, admin role updates, incidents, tickets, evidence notes, and remediation tasks.
- Sensitive normal and error response safety, including absence of passwords, password hashes, secrets, authorization headers, stack traces, SQLAlchemy internals, and raw exception names.
- Audit redaction regressions for auth flows, logout, domain writes, and failed unauthorized writes.
- SQLAlchemy ORM/no raw SQL safety checks over application source.
- Nested-resource IDOR, parent mismatch, soft-delete, inactive assignee/owner, analyst evidence ownership, and read-only role write-denial regressions.
- OpenAPI security metadata, expected endpoint presence, production docs disablement, and absence of password hashes or secret settings in generated schemas.
- Continued absence of new business/domain workflows, CI, git, publishing, tags, releases, and branch protection work.

## Phase 10 Tests

Phase 10 adds tests for:

- STRIDE threat model existence, categories, assets, trust boundaries, mitigations, residual risks, and limitations.
- API reference existence, implemented endpoint coverage, RBAC/authentication documentation, audit behavior, and metadata-only attachment documentation.
- OpenAPI export script output, bearer auth scheme, path consistency with app factory schema, and production docs disable behavior.
- Documentation safety checks for real-looking JWTs, API keys, database password URLs, non-placeholder bearer values, and premature CI/publishing/release/branch-protection claims.
- Endpoint consistency between implemented FastAPI routes and `docs/api_reference.md`.
- Continued absence of new business/domain workflows, CI, git, GitHub Issues, GitHub Projects, publishing, tags, releases, and branch protection work.

## Phase 11 Tests

Phase 11 adds tests for:

- GitHub Actions CI workflow existence, triggers, Python 3.11 usage, stable job names, coverage gate at 95, pytest coverage command, Ruff checks, OpenAPI export, docs safety script, API smoke commands, Alembic smoke commands, and absence of external services.
- CodeQL workflow existence, Python language configuration, stable job name, security-and-quality queries, workflow dispatch, and weekly schedule.
- Dependabot configuration for weekly pip and GitHub Actions updates only.
- Documentation safety script execution and rejection of unsafe temporary content through script helpers.
- Workflow files avoiding hosted-success, publishing, release, tag, and branch-protection claims.

## Phase 12 Tests

Phase 12 adds tests for:

- Release material existence, pending hosted checks, publishing-command documentation, release draft, LinkedIn/CV drafts, and recruiter-facing summary.
- Release checklist tracking local QA and pending publishing, hosted CI, hosted CodeQL, code scanning, secret scanning, Dependabot, live Issues/Projects, branch protection, tag, and release work.
- Local Agile material existence, F1-F14 backlog coverage, planned board columns, planned labels, and no fake board screenshot.
- `CONTRIBUTING.md` defensive-only policy, branch strategy, docs safety command, and quality commands.
- Documentation safety script coverage for `RELEASE.md`, `CONTRIBUTING.md`, Agile docs, and the release checklist.

## Test Types

### Unit Tests

Unit tests should cover password policy, token helper logic, RBAC decision helpers, schema validation, audit redaction helpers, and service-layer rules.

### Integration Tests

Integration tests should exercise API flows through FastAPI's test client or async HTTP client against a test database.

### Security Tests

Security tests should verify denied actions, token misuse, expired tokens, revoked refresh tokens, sensitive field exclusion, rate limit behavior, and production configuration toggles.

## Database Testing Strategy

Tests should use isolated SQLite databases. Test setup must avoid depending on local developer state. Later phases should decide between transaction rollbacks, per-test database creation, or controlled fixture scopes.

## CI Strategy

Planned CI should run:

- Formatting check.
- Linting.
- Type-oriented checks if configured.
- Unit tests.
- Integration tests.
- Coverage report with threshold enforcement.
- Security-focused tests.

## Design Cautions

- Rate limiting should be configurable so tests are deterministic.
- Token expiry tests should avoid flaky real-time sleeps where possible.
- Audit tests should assert redaction and absence of sensitive fields.
- Tests must not require network access or real external services.
