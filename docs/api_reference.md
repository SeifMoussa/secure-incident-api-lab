# API Reference

This reference documents the implemented Secure Incident Management API endpoints as of Phase 10. All examples use placeholders only. Do not use real credentials, real tokens, real customer incident data, or real evidence files.

Use bearer authentication for protected endpoints:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

## Common Security Behavior

- Request bodies use strict schemas and reject unexpected fields.
- Validation errors return a safe generic 422 message.
- Password hashes, raw credentials, authorization headers, API keys, JWT secrets, and internal exceptions are excluded from normal responses.
- Write requests are audit-logged by middleware where applicable.
- Evidence attachments are metadata only. No binary upload or file storage endpoint exists.
- Pagination uses `page` and `page_size`; `page >= 1`, `1 <= page_size <= 100`.

## Role Summary

| Role | Summary |
| --- | --- |
| ADMIN | User management, incident management, nested workflow management, audit reads |
| ANALYST | Incident and nested workflow create/update access, with evidence ownership limits |
| VIEWER | Read-only operational access |
| AUDITOR | Read-only operational access plus audit log reads |

## General

### GET /

Purpose: Service landing response.

Authentication: Not required.

Allowed roles: Public.

Request summary: No body.

Response summary: Service name and safe message.

Validation notes: None.

Security notes: Security headers are applied.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /
```

Example response:

```json
{"service":"Secure Incident Management API","message":"Secure Incident Management API scaffold is running."}
```

### GET /health

Purpose: Local health check.

Authentication: Not required.

Allowed roles: Public.

Request summary: No body.

Response summary: Service health, environment, debug flag, and docs flag.

Validation notes: None.

Security notes: Security headers are applied.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /health
```

Example response:

```json
{"status":"ok","service":"Secure Incident Management API","environment":"test","debug":true,"docs_enabled":true}
```

## Authentication

Purpose: User registration, login, refresh, logout, and profile retrieval.

Authentication requirements: Register, login, refresh, and logout accept request bodies without bearer auth. `/auth/me` requires bearer auth.

Allowed roles: Any active authenticated role can use `/auth/me`. Token issuance depends on valid credentials and active user state.

Security notes: Passwords are accepted only as request inputs and are never returned. Access and refresh tokens are returned only by token issuance endpoints.

### POST /auth/register

Request summary: Email, display name, and credential secret.

Validation notes: Strict body, email validation, password policy, common-password rejection, no role assignment accepted.

Audit behavior: Audited as `CREATE` on `auth`.

Example request:

```http
POST /auth/register
Content-Type: application/json

{"email":"<USER_EMAIL>","password":"<PASSWORD_PLACEHOLDER>","display_name":"<DISPLAY_NAME>"}
```

Example response:

```json
{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"VIEWER","is_active":true}
```

### POST /auth/login

Request summary: Email and credential secret.

Validation notes: Strict body and email validation.

Audit behavior: Audited as `LOGIN`.

Example request:

```http
POST /auth/login
Content-Type: application/json

{"email":"<USER_EMAIL>","password":"<PASSWORD_PLACEHOLDER>"}
```

Example response:

```json
{"access_token":"<ACCESS_TOKEN>","refresh_token":"<REFRESH_TOKEN>","token_type":"bearer"}
```

### POST /auth/refresh

Request summary: Refresh token.

Validation notes: Strict body. Token type and blocklist are checked.

Audit behavior: Not audited by the write-audit middleware configuration.

Example request:

```http
POST /auth/refresh
Content-Type: application/json

{"refresh_token":"<REFRESH_TOKEN>"}
```

Example response:

```json
{"access_token":"<ACCESS_TOKEN>","token_type":"bearer"}
```

### POST /auth/logout

Request summary: Refresh token to blocklist.

Validation notes: Strict body. Raw refresh token is not stored.

Audit behavior: Audited as `LOGOUT`.

Example request:

```http
POST /auth/logout
Content-Type: application/json

{"refresh_token":"<REFRESH_TOKEN>"}
```

Example response:

```json
{"message":"Logged out."}
```

### GET /auth/me

Request summary: Bearer token only.

Validation notes: Requires a valid access token for an active user.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /auth/me
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"ANALYST","is_active":true}
```

## Admin

Purpose: ADMIN-only user management.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN only.

Security notes: Responses exclude password hashes and token material. Admin self-role-change and self-deactivation are blocked.

### GET /admin/users/

Request summary: Optional pagination query parameters.

Response summary: Paginated safe user profiles.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /admin/users/?page=1&page_size=20
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"VIEWER","is_active":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}],"page":1,"page_size":20,"total":1}
```

### GET /admin/users/{uid}

Request summary: User ID path parameter.

Response summary: Safe user profile.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /admin/users/<USER_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"VIEWER","is_active":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}
```

### PATCH /admin/users/{uid}/role

Request summary: New role.

Validation notes: Strict body. Role must be one of `ADMIN`, `ANALYST`, `VIEWER`, `AUDITOR`.

Audit behavior: Audited as `UPDATE` on `user`.

Example request:

```http
PATCH /admin/users/<USER_ID>/role
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"role":"ANALYST"}
```

Example response:

```json
{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"ANALYST","is_active":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}
```

### DELETE /admin/users/{uid}

Request summary: User ID path parameter.

Response summary: Deactivation message and safe user profile.

Audit behavior: Audited as `DELETE` on `user`.

Example request:

```http
DELETE /admin/users/<USER_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"message":"User deactivated.","user":{"user_id":"<USER_ID>","email":"<USER_EMAIL>","display_name":"<DISPLAY_NAME>","role":"VIEWER","is_active":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}}
```

## Incidents

Purpose: Manage synthetic incident records.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN and ANALYST can create/update. ADMIN can delete. ADMIN, ANALYST, VIEWER, and AUDITOR can read and view timeline.

Security notes: Soft-deleted incidents are excluded from normal reads and nested workflows.

### POST /incidents/

Request summary: Title, description, severity, optional status, assignment, MITRE fields, and tags.

Validation notes: Strict body, enum validation, UUID-like assignment validation, MITRE tactic allowlist, MITRE technique pattern, tag limits.

Audit behavior: Audited as `CREATE` on `incident`.

Example request:

```http
POST /incidents/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"title":"<INCIDENT_TITLE>","description":"<INCIDENT_DESCRIPTION>","severity":"HIGH","status":"OPEN","assigned_to":"<USER_ID>","mitre_tactic":"initial-access","mitre_technique":"T0000","tags":["<TAG>"]}
```

Example response:

```json
{"incident_id":"<INCIDENT_ID>","title":"<INCIDENT_TITLE>","description":"<INCIDENT_DESCRIPTION>","severity":"HIGH","status":"OPEN","created_by":"<USER_ID>","assigned_to":"<USER_ID>","mitre_tactic":"initial-access","mitre_technique":"T0000","tags":["<TAG>"],"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}
```

### GET /incidents/

Request summary: Optional pagination and filters: `severity`, `status`, `assigned_to`, `created_after`, `created_before`, `tag`.

Response summary: Paginated incident list.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/?page=1&page_size=20&status=OPEN
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"incident_id":"<INCIDENT_ID>","title":"<INCIDENT_TITLE>","description":"<INCIDENT_DESCRIPTION>","severity":"HIGH","status":"OPEN","created_by":"<USER_ID>","assigned_to":null,"mitre_tactic":null,"mitre_technique":null,"tags":[],"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}],"page":1,"page_size":20,"total":1}
```

### GET /incidents/{incident_id}

Request summary: Incident ID path parameter.

Response summary: One active incident.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response: Same incident object shape as `POST /incidents/`.

### PATCH /incidents/{incident_id}

Request summary: Partial incident update.

Validation notes: Strict body. Server-managed fields are rejected.

Audit behavior: Audited as `UPDATE` on `incident`.

Example request:

```http
PATCH /incidents/<INCIDENT_ID>
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"status":"CONTAINED","tags":["<TAG>"]}
```

Example response: Same incident object shape as `POST /incidents/`.

### DELETE /incidents/{incident_id}

Request summary: Incident ID path parameter.

Response summary: Soft-delete message and incident object.

Audit behavior: Audited as `DELETE` on `incident`.

Example request:

```http
DELETE /incidents/<INCIDENT_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"message":"Incident deleted.","incident":{"incident_id":"<INCIDENT_ID>","title":"<INCIDENT_TITLE>","description":"<INCIDENT_DESCRIPTION>","severity":"HIGH","status":"OPEN","created_by":"<USER_ID>","assigned_to":null,"mitre_tactic":null,"mitre_technique":null,"tags":[],"is_deleted":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}}
```

### GET /incidents/{incident_id}/timeline

Request summary: Incident ID path parameter.

Response summary: Oldest-first sanitized incident audit entries.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/timeline
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"incident_id":"<INCIDENT_ID>","items":[{"audit_id":"<AUDIT_ID>","actor_id":"<USER_ID>","action":"CREATE","resource_type":"incident","resource_id":"<INCIDENT_ID>","timestamp":"<ISO_DATETIME>","ip_address":"<IP_ADDRESS>","changes":{"fields_changed":["title"]},"outcome":"SUCCESS"}],"total":1}
```

## Tickets

Purpose: Manage synthetic tickets nested under active incidents.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN and ANALYST can create/update/delete. ADMIN, ANALYST, VIEWER, and AUDITOR can read.

Security notes: Ticket IDs are scoped to the parent incident. Wrong parent IDs and soft-deleted resources return safe not-found responses.

### POST /incidents/{incident_id}/tickets/

Audit behavior: Audited as `CREATE` on `ticket`.

Example request:

```http
POST /incidents/<INCIDENT_ID>/tickets/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"title":"<TICKET_TITLE>","description":"<TICKET_DESCRIPTION>","status":"OPEN","priority":"P2","assigned_to":"<USER_ID>","due_date":"<ISO_DATETIME>"}
```

Example response:

```json
{"ticket_id":"<TICKET_ID>","incident_id":"<INCIDENT_ID>","title":"<TICKET_TITLE>","description":"<TICKET_DESCRIPTION>","status":"OPEN","priority":"P2","assigned_to":"<USER_ID>","due_date":"<ISO_DATETIME>","created_by":"<USER_ID>","is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}
```

### GET /incidents/{incident_id}/tickets/

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/tickets/?page=1&page_size=20
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"ticket_id":"<TICKET_ID>","incident_id":"<INCIDENT_ID>","title":"<TICKET_TITLE>","description":"<TICKET_DESCRIPTION>","status":"OPEN","priority":"P2","assigned_to":null,"due_date":null,"created_by":"<USER_ID>","is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}],"page":1,"page_size":20,"total":1}
```

### GET /incidents/{incident_id}/tickets/{ticket_id}

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/tickets/<TICKET_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response: Same ticket object shape as `POST /incidents/{incident_id}/tickets/`.

### PATCH /incidents/{incident_id}/tickets/{ticket_id}

Validation notes: Strict body. Server-managed fields are rejected.

Audit behavior: Audited as `UPDATE` on `ticket`.

Example request:

```http
PATCH /incidents/<INCIDENT_ID>/tickets/<TICKET_ID>
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"status":"DONE","priority":"P3"}
```

Example response: Same ticket object shape as `POST /incidents/{incident_id}/tickets/`.

### DELETE /incidents/{incident_id}/tickets/{ticket_id}

Audit behavior: Audited as `DELETE` on `ticket`.

Example request:

```http
DELETE /incidents/<INCIDENT_ID>/tickets/<TICKET_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"message":"Ticket deleted.","ticket":{"ticket_id":"<TICKET_ID>","incident_id":"<INCIDENT_ID>","title":"<TICKET_TITLE>","description":"<TICKET_DESCRIPTION>","status":"OPEN","priority":"P2","assigned_to":null,"due_date":null,"created_by":"<USER_ID>","is_deleted":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}}
```

## Evidence

Purpose: Manage synthetic evidence notes and metadata-only attachments.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN and ANALYST can create. ADMIN can delete. ANALYST can update own notes only. ADMIN, ANALYST, VIEWER, and AUDITOR can read.

Security notes: No binary upload, disk file reading, or file storage exists. Attachment metadata validates filename, content type, size, and storage reference shape.

### POST /incidents/{incident_id}/evidence/

Audit behavior: Audited as `CREATE` on `evidence`.

Example request:

```http
POST /incidents/<INCIDENT_ID>/evidence/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"content":"<EVIDENCE_NOTE>","source":"<EVIDENCE_SOURCE>","collected_at":"<ISO_DATETIME>","tags":["<TAG>"],"attachments":[{"filename":"<FILENAME>","content_type":"text/plain","size_bytes":1,"storage_reference":"<METADATA_REFERENCE>"}]}
```

Example response:

```json
{"evidence_id":"<EVIDENCE_ID>","incident_id":"<INCIDENT_ID>","content":"<EVIDENCE_NOTE>","source":"<EVIDENCE_SOURCE>","collected_at":"<ISO_DATETIME>","created_by":"<USER_ID>","tags":["<TAG>"],"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>","attachments":[{"attachment_id":"<ATTACHMENT_ID>","filename":"<FILENAME>","content_type":"text/plain","size_bytes":1,"storage_reference":"<METADATA_REFERENCE>","created_at":"<ISO_DATETIME>"}]}
```

### GET /incidents/{incident_id}/evidence/

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/evidence/?page=1&page_size=20
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"evidence_id":"<EVIDENCE_ID>","incident_id":"<INCIDENT_ID>","content":"<EVIDENCE_NOTE>","source":"<EVIDENCE_SOURCE>","collected_at":"<ISO_DATETIME>","created_by":"<USER_ID>","tags":[],"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>","attachments":[]}],"page":1,"page_size":20,"total":1}
```

### GET /incidents/{incident_id}/evidence/{evidence_id}

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/evidence/<EVIDENCE_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response: Same evidence object shape as `POST /incidents/{incident_id}/evidence/`.

### PATCH /incidents/{incident_id}/evidence/{evidence_id}

Validation notes: Strict body. Server-managed fields are rejected.

Audit behavior: Audited as `UPDATE` on `evidence`.

Example request:

```http
PATCH /incidents/<INCIDENT_ID>/evidence/<EVIDENCE_ID>
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"source":"<UPDATED_EVIDENCE_SOURCE>","tags":["<TAG>"]}
```

Example response: Same evidence object shape as `POST /incidents/{incident_id}/evidence/`.

### DELETE /incidents/{incident_id}/evidence/{evidence_id}

Audit behavior: Audited as `DELETE` on `evidence`.

Example request:

```http
DELETE /incidents/<INCIDENT_ID>/evidence/<EVIDENCE_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"message":"Evidence note deleted.","evidence":{"evidence_id":"<EVIDENCE_ID>","incident_id":"<INCIDENT_ID>","content":"<EVIDENCE_NOTE>","source":"<EVIDENCE_SOURCE>","collected_at":"<ISO_DATETIME>","created_by":"<USER_ID>","tags":[],"is_deleted":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>","attachments":[]}}
```

## Remediation

Purpose: Manage remediation tasks nested under active incidents.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN and ANALYST can create/update/delete. ADMIN, ANALYST, VIEWER, and AUDITOR can read.

Security notes: Owner IDs must reference active users when provided. `completed_at` is server-managed.

### POST /incidents/{incident_id}/remediation/

Audit behavior: Audited as `CREATE` on `remediation`.

Example request:

```http
POST /incidents/<INCIDENT_ID>/remediation/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"action":"<REMEDIATION_ACTION>","owner":"<USER_ID>","status":"PENDING","deadline":"<ISO_DATETIME>","completion_notes":"<COMPLETION_NOTES>"}
```

Example response:

```json
{"task_id":"<TASK_ID>","incident_id":"<INCIDENT_ID>","action":"<REMEDIATION_ACTION>","owner":"<USER_ID>","status":"PENDING","deadline":"<ISO_DATETIME>","completion_notes":"<COMPLETION_NOTES>","completed_at":null,"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}
```

### GET /incidents/{incident_id}/remediation/

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /incidents/<INCIDENT_ID>/remediation/?page=1&page_size=20
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"task_id":"<TASK_ID>","incident_id":"<INCIDENT_ID>","action":"<REMEDIATION_ACTION>","owner":null,"status":"PENDING","deadline":null,"completion_notes":null,"completed_at":null,"is_deleted":false,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}],"page":1,"page_size":20,"total":1}
```

### PATCH /incidents/{incident_id}/remediation/{task_id}

Validation notes: Strict body. `completed_at` is server-managed and rejected from client input.

Audit behavior: Audited as `UPDATE` on `remediation`.

Example request:

```http
PATCH /incidents/<INCIDENT_ID>/remediation/<TASK_ID>
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"status":"COMPLETE","completion_notes":"<COMPLETION_NOTES>"}
```

Example response: Same remediation object shape as `POST /incidents/{incident_id}/remediation/`.

### DELETE /incidents/{incident_id}/remediation/{task_id}

Audit behavior: Audited as `DELETE` on `remediation`.

Example request:

```http
DELETE /incidents/<INCIDENT_ID>/remediation/<TASK_ID>
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"message":"Remediation task deleted.","task":{"task_id":"<TASK_ID>","incident_id":"<INCIDENT_ID>","action":"<REMEDIATION_ACTION>","owner":null,"status":"PENDING","deadline":null,"completion_notes":null,"completed_at":null,"is_deleted":true,"created_at":"<ISO_DATETIME>","updated_at":"<ISO_DATETIME>"}}
```

## Audit

Purpose: Read sanitized append-only audit entries.

Authentication requirement: Bearer token required.

Allowed roles: ADMIN and AUDITOR.

Security notes: Audit entries are sanitized. No audit mutation routes exist. Filters include resource type, resource ID, actor, action, and outcome.

### GET /audit/

Request summary: Optional pagination and filters.

Response summary: Newest-first paginated audit entries.

Audit behavior: Not audited because it is a read.

Example request:

```http
GET /audit/?page=1&page_size=20&resource_type=incident&outcome=SUCCESS
Authorization: Bearer <ACCESS_TOKEN>
```

Example response:

```json
{"items":[{"audit_id":"<AUDIT_ID>","actor_id":"<USER_ID>","action":"CREATE","resource_type":"incident","resource_id":"<INCIDENT_ID>","timestamp":"<ISO_DATETIME>","ip_address":"<IP_ADDRESS>","changes":{"fields_changed":["title"]},"outcome":"SUCCESS"}],"page":1,"page_size":20,"total":1}
```

## Limitations

- This is a production-pattern portfolio lab, not a deployed production SOC platform.
- No real credentials, tokens, customer incidents, or evidence files should be used.
- Evidence attachments remain metadata only.
- CI, CodeQL, publishing, releases, branch protection, and GitHub project management are not implemented in Phase 10.
