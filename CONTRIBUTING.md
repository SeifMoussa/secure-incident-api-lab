# Contributing

This repository is a defensive portfolio lab. Contributions must preserve the safety scope.

## Defensive-Only Policy

Do not add:

- Offensive tooling.
- Exploit code.
- Malware behavior.
- Live scanning.
- Credential harvesting.
- Real credentials.
- Real access tokens or refresh tokens.
- Real API keys or database passwords.
- Real customer incident data.
- Real evidence files.
- Binary evidence upload or file storage behavior.

Use synthetic/demo data and placeholders such as `<ACCESS_TOKEN>`, `<REFRESH_TOKEN>`, `<USER_ID>`, and `<INCIDENT_ID>`.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Branch Strategy

- `main`: protected after publishing.
- `feature/<short-name>`: feature or documentation work.
- `release/<version>`: release preparation after local QA.

## Pull Request Checklist

- [ ] Scope is defensive and uses synthetic/demo data only.
- [ ] No real credentials, tokens, API keys, secrets, or customer data.
- [ ] No offensive behavior, exploit code, live scanning, or malware behavior.
- [ ] Tests added or updated where behavior changes.
- [ ] Documentation updated where relevant.
- [ ] OpenAPI export updated when schema changes.
- [ ] Docs safety script passes.
- [ ] Ruff check and format check pass.
- [ ] Coverage gate remains at or above 95%.

## Testing Commands

```bash
python scripts/export_openapi.py
python scripts/check-docs.py
python -m pytest
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95
python -m ruff check .
python -m ruff format --check .
python -m alembic upgrade head
python -m alembic current
```

## Security Reporting

This is a portfolio lab and is not deployed as a production service. For security concerns in the repository content, open a private report or contact the maintainer after the repository is published. Do not include real secrets, tokens, or customer data in reports.
