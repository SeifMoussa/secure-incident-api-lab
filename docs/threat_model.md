# STRIDE Threat Model

## Project Overview

Secure Incident Management API is a defensive, production-pattern portfolio lab built with FastAPI. It manages synthetic incident records, tickets, evidence notes, attachment metadata, remediation tasks, users, roles, and audit logs. It is not a deployed production SOC platform and does not perform live scanning, exploitation, packet capture, malware behavior, or real incident response operations.

## Security Scope

The threat model covers the API application, authentication, authorization, validation, audit logging, security middleware, and database access patterns. It covers development, test, and local demonstration use with synthetic/demo data only.

It does not cover cloud infrastructure, a real production deployment, organization-specific compliance requirements, operational monitoring, disaster recovery, SIEM integration, or real SOC processes.

## Assets

- User credentials.
- Password hashes.
- Access tokens.
- Refresh-token JTIs and blocklist entries.
- Incident data.
- Ticket data.
- Evidence notes.
- Attachment metadata.
- Remediation tasks.
- Audit logs.
- Admin role-management capability.
- API configuration and secrets.

## Trust Boundaries

- Client to API: HTTP clients submit requests to FastAPI endpoints.
- API to database: application services use SQLAlchemy ORM to read and write SQLite-compatible tables.
- Authenticated user to protected endpoints: bearer-token authentication gates protected routes.
- ADMIN to user-management endpoints: ADMIN-only dependencies gate role updates and deactivation.
- AUDITOR to audit logs: ADMIN and AUDITOR can read audit entries; audit mutation routes do not exist.
- Local/dev/test environment boundaries: local settings, test fixtures, local SQLite, and generated docs are not production environments.

## Security Assumptions

- Test data is synthetic/demo only.
- JWT signing secrets are environment-backed and production settings reject placeholders.
- Clients keep tokens confidential.
- The database is reachable only by the application in the intended local/test setup.
- Rate limiting is local in-memory and suitable for this lab, not a distributed deployment.
- Evidence attachments are metadata only; binary upload and file storage are out of scope.

## Out of Scope

- Offensive security tooling.
- Exploit code.
- Live scanning.
- Malware behavior.
- Real credentials, real tokens, real incident data, or real evidence files.
- Binary evidence upload, disk file reading, or file storage.
- Production deployment claims.
- CI, CodeQL, publishing, tags, releases, and branch protection until later phases.

## STRIDE Summary

| Category | Example Threats | Existing Mitigations | Residual Risk |
| --- | --- | --- | --- |
| Spoofing | Stolen bearer token, forged auth header, inactive user reuse | JWT validation, token type checks, current active database user lookup, refresh-token blocklist | Token theft cannot be fully prevented without client/device controls |
| Tampering | Client changes server-managed fields, nested resource ID mismatch, soft-deleted record mutation | Strict Pydantic schemas, mass-assignment tests, service-layer parent scoping, soft-delete exclusion | Middleware cannot provide perfect semantic diffs for every update |
| Repudiation | User denies write action, failed writes are not traceable | Middleware-driven audit logging for write requests, actor attribution when available, append-only audit API | No external immutable log store or request correlation IDs yet |
| Information Disclosure | Sensitive fields in responses, validation errors, audit logs, OpenAPI, CORS | Safe response schemas, generic validation errors, audit sanitizer, CORS allowlist, production docs disabled, security regression tests | Auth token responses intentionally return tokens to the caller |
| Denial of Service | Login brute force, high request volume, oversized lists | Login/general rate limiting, bounded pagination, request field length limits | In-memory limiter is not distributed and resets with process restart |
| Elevation of Privilege | Role escalation, stale role claims, user self-admin abuse | ADMIN-only role routes, current database role checks, self-role-change/deactivation protections, RBAC tests | Fine-grained tenant isolation is not modeled in this lab |

## Threats And Mitigations

### Token Theft

Threat: An attacker obtains an access token and attempts to call protected endpoints.

Mitigations: Access tokens are typed and time-limited. Protected endpoints require bearer authentication. Authorization checks use the current database user state so inactive users and changed roles take effect.

Residual risk: The API cannot fully protect against compromise of the client environment.

### Brute-Force Login

Threat: Repeated login attempts target an account.

Mitigations: `/auth/login` is rate-limited by IP in normal configuration. Login failures return a generic message. Password policy and common-password rejection reduce weak credential risk.

Residual risk: Local in-memory rate limiting is not a replacement for a distributed production rate-limit service.

### Weak Passwords

Threat: Users choose weak or common secrets.

Mitigations: Password policy enforces length and character requirements and rejects a local common-password list. Passwords are hashed and never returned in response schemas.

Residual risk: The lab does not include compromised-password intelligence feeds.

### Refresh-Token Replay

Threat: A refresh token is reused after logout.

Mitigations: Refresh tokens include a JTI. Logout blocklists the refresh-token JTI. Refresh validates token type and blocklist state.

Residual risk: The lab uses local database state and does not implement device/session management.

### IDOR On Nested Resources

Threat: A user requests a ticket, evidence note, or remediation task under the wrong incident.

Mitigations: Services check the active parent incident and verify nested resource ownership by incident ID. Wrong parent IDs return safe not-found responses.

Residual risk: Cross-tenant authorization is not modeled because this lab does not implement tenancy.

### Role Escalation

Threat: A client attempts to set role fields during registration or update another user's role without ADMIN privileges.

Mitigations: Registration forbids unexpected role fields. Role updates are ADMIN-only. Admin self-role-change is blocked.

Residual risk: Administrative actions still require careful operational controls outside the lab.

### Mass Assignment

Threat: A client sends server-managed fields such as `created_by`, `is_deleted`, IDs, or audit fields.

Mitigations: Strict schemas forbid extra fields. Phase 9 tests cover registration, admin role updates, incidents, tickets, evidence notes, and remediation tasks.

Residual risk: Future schemas must preserve strict extra-field rejection.

### SQL Injection

Threat: User input is concatenated into SQL.

Mitigations: Application code uses SQLAlchemy ORM/query builder patterns. Static tests check app source for raw SQL construction patterns.

Residual risk: Static checks are conservative and should be revisited if hand-written SQL is ever introduced.

### Audit Log Tampering

Threat: A client modifies or deletes audit entries.

Mitigations: Audit logs have a read-only API surface. No audit POST, PATCH, or DELETE routes exist. Audit entries are written by middleware for write requests.

Residual risk: Database administrators could still alter local database state outside the API.

### Sensitive Data Leakage In Validation Errors

Threat: Validation errors echo submitted request bodies or protected field names.

Mitigations: A centralized validation error handler returns a generic safe 422 message and does not echo submitted bodies.

Residual risk: Future custom exception handlers must preserve this behavior.

### Sensitive Data Leakage In Audit Logs

Threat: Passwords, tokens, authorization headers, cookies, API keys, or secret-like values are stored in audit entries.

Mitigations: Audit changes are conservative field summaries. The sanitizer recursively redacts sensitive keys and token-like values. Regression tests cover auth and domain write flows.

Residual risk: Middleware-level summaries cannot guarantee perfect business diffs.

### CORS Misconfiguration

Threat: Browser clients from unexpected origins can interact with the API.

Mitigations: CORS uses an explicit allowlist. Wildcard origins are not enabled by default. Production defaults to an empty allowlist unless origins are configured.

Residual risk: Real deployment origin management is outside the lab.

### Missing Security Headers

Threat: Responses lack browser-relevant defensive headers.

Mitigations: Security middleware applies content type, frame, XSS, referrer, cache, CSP, and production HSTS headers where appropriate.

Residual risk: Header policies may need adjustment for a real deployed UI.

### Rate-Limit Bypass

Threat: High-volume requests avoid local rate limits through distributed sources or process restarts.

Mitigations: Login and general endpoints are rate-limited per IP in normal local configuration.

Residual risk: The in-memory limiter is not distributed and is not claimed as production-ready.

### Soft-Deleted Data Exposure

Threat: Soft-deleted incidents or nested resources remain visible or mutable.

Mitigations: Service-layer lookups exclude soft-deleted parents and resources. Tests cover detail, update, delete, and nested access.

Residual risk: Database access outside the API can still inspect soft-deleted rows.

### Production Docs Exposure

Threat: Interactive docs expose API structure in production configuration.

Mitigations: Production settings disable `/docs`, `/redoc`, and `/openapi.json`. Tests verify this behavior.

Residual risk: Generated local documentation files are still present in the repository for review.

### Attachment Upload And File Handling Risk

Threat: Evidence attachment handling leads to path traversal, unsafe file reads, or binary storage risk.

Mitigations: Attachments are metadata only. No binary upload, disk file reading, or file storage behavior exists. Filename and content-type metadata are validated.

Residual risk: Adding real file handling would require a separate design and threat model update.

## Residual Risks And Limitations

- This is a portfolio lab, not a deployed production SOC platform.
- SQLite is used for local development and tests; production database operations are not modeled.
- In-memory rate limiting is not suitable for multi-process or distributed production environments.
- Audit logs are append-only at the API level but not protected by an external immutable log store.
- No request correlation IDs, centralized logging, monitoring, alerting, backup, or disaster recovery are implemented.
- Hosted CI/CodeQL re-verification, live Dependabot PR review, branch protection, and release governance remain pending.

## Future Hardening Ideas

- Add request correlation IDs and structured security event logging.
- Use a distributed rate limiter for multi-instance deployments.
- Add external immutable audit storage or signed audit records.
- Add dependency scanning and CodeQL in CI.
- Add tenant-aware authorization if multi-tenant behavior is introduced.
- Add formal API reference generation and versioned release documentation.
- Revisit CSP and CORS policies when a real UI exists.
