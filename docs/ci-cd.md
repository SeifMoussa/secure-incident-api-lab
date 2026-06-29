# CI/CD Configuration

Phase 11 added repository configuration for GitHub Actions CI, CodeQL, Dependabot, and documentation safety checks. The repository is published. The latest hosted CI run completed Docs Safety Checks and API Smoke successfully but failed Tests on stale route-inspection assumptions; hosted CI has not passed after the local audit fixes yet.

## CI Workflow

`.github/workflows/ci.yml` defines three stable jobs:

- Tests
- Docs Safety Checks
- API Smoke

The Tests job installs the package with development dependencies, runs pytest with coverage, enforces `--cov-fail-under=95`, and runs Ruff lint and format checks.

The Docs Safety Checks job exports OpenAPI, runs the documentation safety script, and compiles the documentation scripts.

The API Smoke job runs safe local commands only: Uvicorn factory help, OpenAPI export, and Alembic upgrade/current against local SQLite settings. It does not start a live server and does not require PostgreSQL or network services.

## CodeQL

`.github/workflows/codeql.yml` configures CodeQL for Python using security-and-quality queries. Code scanning is available because the repository is public. The Phase 13A audit corrected the real side-effect-in-assert test findings locally; reports against Alembic's required revision metadata and imports guarded by `TYPE_CHECKING` were reviewed as non-runtime framework/static-analysis patterns. Hosted CodeQL verification pending until the next pushed run completes.

## Dependabot

`.github/dependabot.yml` configures weekly updates for Python packages and GitHub Actions only. GitHub has recognized both configured ecosystems.

## Documentation Safety

`scripts/check-docs.py` validates required documentation and workflow files, required safety wording, and absence of real-looking secrets, tokens, database password URLs, non-placeholder bearer tokens, and premature hosted CI/release/branch-protection claims.

## Limitations

This remains a production-pattern portfolio lab, not a deployed production SOC platform. The repository is published publicly. Hosted CI/CodeQL re-verification, branch protection, live GitHub Issues, a live GitHub Project board, tags, and releases remain pending.
