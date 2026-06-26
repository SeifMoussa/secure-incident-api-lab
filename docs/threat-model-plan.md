# Threat Model Plan

## Planned Document

Phase 10 should create `docs/threat_model.md` using STRIDE. This Phase 0 file defines the planned structure and scope.

## Scope

The threat model covers the FastAPI backend, database interactions, authentication, authorization, audit logging, API validation, and CI/CD workflow. It does not cover a real production deployment, cloud infrastructure, SOC operations, or live incident response.

## Assets

- User accounts.
- Password hashes.
- Access tokens.
- Refresh tokens and token hashes.
- Incident records.
- Tickets.
- Evidence notes.
- Attachment metadata.
- Remediation tasks.
- Audit logs.
- Configuration secrets.

## Trust Boundaries

- Client to API boundary.
- API router to service layer boundary.
- Service layer to database boundary.
- Authentication token issuance and verification boundary.
- CI environment to repository boundary.
- Configuration environment to application boundary.

## STRIDE Categories

### Spoofing

Planned analysis:

- Token theft or reuse.
- Refresh token replay.
- Deactivated users attempting access.
- Forged authentication headers.

### Tampering

Planned analysis:

- Unauthorized incident or ticket updates.
- Audit log modification attempts.
- Client-side manipulation of role fields.
- Soft-deleted record mutation.

### Repudiation

Planned analysis:

- Missing audit entries for write actions.
- Insufficient actor attribution.
- Lack of request correlation identifiers.
- Ambiguous service-layer diffs.

### Information Disclosure

Planned analysis:

- Passwords or token values leaking in responses.
- Authorization headers leaking to logs.
- Sensitive fields leaking to audit entries.
- Overbroad CORS.
- Docs exposed in production configuration.

### Denial of Service

Planned analysis:

- Authentication brute force.
- High-volume write requests.
- Expensive list queries without pagination.
- Oversized request bodies or markdown fields.

### Elevation of Privilege

Planned analysis:

- Role change abuse.
- Missing RBAC checks.
- Token claims trusted without database user validation.
- Inactive user access.

## Planned Mitigations

- Short-lived access tokens.
- Hashed refresh token storage.
- Refresh token blocklist.
- Password hashing and password policy.
- Common password rejection.
- Centralized RBAC dependencies and service-layer checks.
- Strict Pydantic validation.
- Pagination bounds.
- Rate limiting.
- Security headers.
- CORS allowlist.
- Production docs toggle.
- Append-only audit API.
- Audit redaction allowlist.
- CI test enforcement.
- CodeQL and Dependabot.

## Residual Risks

- This lab does not include full production monitoring or incident response operations.
- SQLite differs from PostgreSQL in concurrency and some constraint behavior.
- Middleware-only audit diffing is insufficient for perfect semantic changes.
- Threat model must be revisited after implementation details are known.
