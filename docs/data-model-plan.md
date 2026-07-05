# Data Model Plan

## Database Strategy

The database layer uses SQLAlchemy ORM with Alembic migrations. Development and tests use SQLite. Models are designed to remain PostgreSQL-compatible so the project can demonstrate a realistic migration path without requiring PostgreSQL during early local development.

Raw SQL strings are out of scope. Query behavior should use SQLAlchemy ORM expressions.

The database foundation includes ORM models, database-safe enums, and a baseline migration. This layer does not implement service-layer business behavior or API endpoints for these models.

Authentication uses the `users` and `token_blocklist` tables. It does not add seed users, real credentials, or domain service behavior.

ADMIN-only user management uses the existing `users` table. Deactivation is represented by `is_active=false`; no hard-delete user behavior is implemented.

Incident CRUD uses the existing `incidents` table. Deletion is represented by `is_deleted=true`; hard delete is not implemented. Incident timeline was deferred at this design milestone.

Ticket, evidence, and remediation workflows use the existing `tickets`, `evidence_notes`, `evidence_attachments`, and `remediation_tasks` tables. Ticket, evidence note, and remediation deletes are soft deletes. Evidence attachments are metadata records only; no binary file content is stored.

Middleware-driven write audit entries and incident timeline reads use the existing `audit_log` table. Audit entries store sanitized summaries and safe metadata only.

Security middleware and settings do not add or change database tables.

Validation hardening and security regression tests do not add or change database tables.

Documentation and OpenAPI export artifacts do not add or change database tables.

Workflow and documentation safety configuration do not add or change database tables.

## Planned Entities

### User

Represents an authenticated user.

Planned fields:

- `id`
- `email`
- `password_hash`
- `role`
- `is_active`
- `created_at`
- `updated_at`
- `deactivated_at`

Sensitive fields such as `password_hash` must never appear in API responses, logs, or audit details.

### Refresh Token

Represents a refresh token record or blocklist entry.

Planned fields:

- `id`
- `user_id`
- `token_hash`
- `expires_at`
- `revoked_at`
- `created_at`
- `last_used_at`

Refresh tokens should be stored hashed. Raw refresh tokens should never be stored.

### Incident

Represents a synthetic security incident.

Planned fields:

- `id`
- `title`
- `description`
- `severity`
- `status`
- `owner_id`
- `created_by_id`
- `created_at`
- `updated_at`
- `deleted_at`

Soft delete is represented by `deleted_at`.

### Ticket

Represents a ticket within an incident.

Planned fields:

- `id`
- `incident_id`
- `title`
- `description`
- `status`
- `assignee_id`
- `created_by_id`
- `created_at`
- `updated_at`
- `deleted_at`

### Evidence Note

Represents a markdown note associated with an incident. Attachments are metadata only.

Planned fields:

- `id`
- `incident_id`
- `title`
- `markdown_content`
- `created_by_id`
- `created_at`
- `updated_at`
- `deleted_at`

### Attachment Metadata

Represents metadata for an evidence attachment. No binary upload or file storage is implemented or planned in the current scope.

Planned fields:

- `id`
- `evidence_note_id`
- `filename`
- `content_type`
- `size_bytes`
- `description`
- `created_at`

### Remediation Task

Represents remediation work associated with an incident.

Planned fields:

- `id`
- `incident_id`
- `title`
- `description`
- `status`
- `assignee_id`
- `created_by_id`
- `due_at`
- `completed_at`
- `created_at`
- `updated_at`

When status becomes `COMPLETE`, `completed_at` should be set. If status changes away from `COMPLETE`, behavior must be explicitly defined during implementation.

### Audit Log

Represents an append-only write audit event.

Implemented fields:

- `audit_id`
- `actor_id`
- `action`
- `resource_type`
- `resource_id`
- `timestamp`
- `ip_address`
- `changes`
- `outcome`

Audit logs must exclude passwords, password hashes, access tokens, refresh tokens, authorization headers, API keys, JWT secrets, cookies, raw tokens, and sensitive secret values. The audit implementation stores conservative changed-field summaries rather than raw request/response bodies.

## Entity Relationship Overview

- User has many incidents as owner.
- User has many incidents as creator.
- User has many tickets as assignee or creator.
- User has many remediation tasks as assignee or creator.
- User has many refresh token records.
- User has many audit logs as actor.
- Incident has many tickets.
- Incident has many evidence notes.
- Incident has many remediation tasks.
- Evidence note has many attachment metadata records.
- Audit log references an entity by type and id to support multiple audited entity types.

## Design Cautions

- Soft-deleted records should be excluded from normal list/detail queries unless explicitly included for authorized administrative or audit views.
- Database uniqueness and indexes should be planned for email, token hash lookups, incident status filters, and audit timestamps.
- Audit logs should be append-only at the API and service layers.
- Models must not rely on database features unavailable in SQLite unless fallback behavior is planned.

## Database Tables

- `users`
- `token_blocklist`
- `incidents`
- `tickets`
- `evidence_notes`
- `evidence_attachments`
- `remediation_tasks`
- `audit_log`
