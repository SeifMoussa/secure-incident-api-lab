# Release Checklist

This checklist tracks local release readiness and pending hosted/publishing work. Pending hosted items must not be marked complete until after publishing.

## Local QA

- [x] Local tests passed.
- [x] Coverage gate passed at 95%.
- [x] Ruff check passed.
- [x] Ruff format check passed.
- [x] Alembic upgrade/current passed against local SQLite.
- [x] OpenAPI export passed.
- [x] Docs safety check passed.

## Publishing Pending

- [ ] Git initialization pending.
- [ ] Repository publishing pending.
- [ ] Hosted CI pending.
- [ ] Hosted CodeQL pending.
- [ ] Code scanning review pending.
- [ ] Secret scanning review pending.
- [ ] Dependabot PR review pending.
- [ ] GitHub Issues creation pending.
- [ ] GitHub Project board creation pending.
- [ ] Branch protection pending.
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
