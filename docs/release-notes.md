# Release Notes

## v0.1.0 - Secure Incident Management API

The initial public release provides a production-pattern FastAPI backend for
synthetic security incident management workflows.

### Highlights

- JWT authentication, refresh-token revocation, password policy, and RBAC.
- Administrative user management and incident, ticket, evidence-note, and
  remediation workflows.
- Metadata-only evidence attachments; no binary upload or file storage.
- Audit logging, incident timelines, security headers, rate limiting, strict
  validation, and an explicit CORS allowlist.
- STRIDE threat model, API reference, OpenAPI export, pytest coverage, Ruff,
  GitHub Actions, CodeQL, and Dependabot configuration.

### Safety Scope

This is a defensive portfolio lab using synthetic/demo data only. It contains
no real credentials, customer incident data, evidence files, exploit code,
live scanning, or malware behavior. It is not a deployed production SOC
platform.

The annotated `v0.1.0` tag exists and the GitHub Release is published.
