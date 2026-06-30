# CI/CD Configuration

Phase 11 added repository configuration for GitHub Actions CI, CodeQL, Dependabot, and documentation safety checks. The repository is published publicly. Hosted CI passed Tests, Docs Safety Checks, and API Smoke at commit `c9f96289`.

## CI Workflow

`.github/workflows/ci.yml` defines three stable jobs:

- Tests
- Docs Safety Checks
- API Smoke

The Tests job installs the package with development dependencies, runs pytest with coverage, enforces `--cov-fail-under=95`, and runs Ruff lint and format checks.

The Docs Safety Checks job exports OpenAPI, runs the documentation safety script, and compiles the documentation scripts.

The API Smoke job runs safe local commands only: Uvicorn factory help, OpenAPI export, and Alembic upgrade/current against local SQLite settings. It does not start a live server and does not require PostgreSQL or network services.

## CodeQL

`.github/workflows/codeql.yml` configures CodeQL for Python using security-and-quality queries. Hosted CodeQL passed at commit `c9f96289`. GitHub reports zero open code-scanning alerts and zero open secret-scanning alerts.

## Dependabot

`.github/dependabot.yml` configures weekly updates for Python packages and GitHub Actions only. GitHub has recognized both configured ecosystems. PRs #1-#4 were reviewed individually in Phase 14. All remain open and unmerged because they cross major/version boundaries and their current Tests checks fail.

## Documentation Safety

`scripts/check-docs.py` validates required documentation and workflow files, required safety wording, accurate Phase 13B hosted/governance status, and absence of real-looking secrets, tokens, database password URLs, non-placeholder bearer tokens, premature release/tag/Project claims, and premature Dependabot merge claims.

## Branch Protection

Protection for `main` is configured and verified. Merges require an up-to-date branch, one approving pull-request review, and successful Tests, Docs Safety Checks, API Smoke, and CodeQL (python) checks. Force pushes and branch deletion are disabled. Administrators retain GitHub's default unenforced setting.

## Limitations

This remains a production-pattern portfolio lab, not a deployed production SOC platform. Live Issues and branch protection are configured. The `v0.1.0` tag exists and the GitHub Release is published. Project board creation is pending because the token lacks project scope, and no Dependabot PR has been merged.
