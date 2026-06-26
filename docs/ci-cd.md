# CI/CD Configuration

Phase 11 adds local repository configuration for GitHub Actions CI, CodeQL, Dependabot, and documentation safety checks. The repository is not published yet, so hosted GitHub CI and hosted CodeQL have not run.

## CI Workflow

`.github/workflows/ci.yml` defines three stable jobs:

- Tests
- Docs Safety Checks
- API Smoke

The Tests job installs the package with development dependencies, runs pytest with coverage, enforces `--cov-fail-under=95`, and runs Ruff lint and format checks.

The Docs Safety Checks job exports OpenAPI, runs the documentation safety script, and compiles the documentation scripts.

The API Smoke job runs safe local commands only: Uvicorn factory help, OpenAPI export, and Alembic upgrade/current against local SQLite settings. It does not start a live server and does not require PostgreSQL or network services.

## CodeQL

`.github/workflows/codeql.yml` configures CodeQL for Python using security-and-quality queries. Hosted CodeQL is not verified until the repository is published and GitHub Actions runs.

## Dependabot

`.github/dependabot.yml` configures weekly updates for Python packages and GitHub Actions only. Dependabot pull requests will only appear after publishing.

## Documentation Safety

`scripts/check-docs.py` validates required documentation and workflow files, required safety wording, and absence of real-looking secrets, tokens, database password URLs, non-placeholder bearer tokens, and premature hosted CI/release/branch-protection claims.

## Limitations

This remains a production-pattern portfolio lab, not a deployed production SOC platform. Phase 12 adds local release and Agile preparation materials only. Branch protection, live GitHub Issues, live GitHub Projects, tags, releases, and publishing are later-phase work.
