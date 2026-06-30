# Release Checklist

This checklist tracks local release readiness after repository publication. Pending hosted items must not be marked complete until verified.

## Local QA

- [x] Local tests passed.
- [x] Coverage gate passed at 95%.
- [x] Ruff check passed.
- [x] Ruff format check passed.
- [x] Alembic upgrade/current passed against local SQLite.
- [x] OpenAPI export passed.
- [x] Docs safety check passed.

## Publishing and Hosted Status

- [x] Git initialization complete.
- [x] Repository publishing complete.
- [x] Public repository visibility confirmed.
- [x] Hosted CI passed at the latest Phase 13B commit.
- [x] Hosted CodeQL passed at the latest Phase 13B commit.
- [x] Open code-scanning alerts confirmed at 0.
- [x] Open secret-scanning alerts confirmed at 0.
- [ ] Dependabot PR review pending.
- [x] GitHub Issues F1-F14 created and left open.
- [ ] Project board creation pending because the token lacks project scope.
- [x] Branch protection configured and verified for `main`.
- [x] Required checks: Tests, Docs Safety Checks, API Smoke, and CodeQL (python).
- [x] One approving pull-request review required; strict/up-to-date checks enabled.
- [x] Force pushes and branch deletion disabled.
- [ ] `v0.1.0` tag pending.
- [ ] GitHub Release pending.

## Safety Review

- [ ] No real credentials.
- [ ] No real tokens.
- [ ] No API keys.
- [ ] No database passwords.
- [ ] No real customer incident data.
- [ ] No real evidence files.
- [ ] No fake Agile board screenshots.
