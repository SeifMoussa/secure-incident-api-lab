# SDLC Plan

## Workflow Overview

The planned workflow uses feature branches, pull requests, automated CI, CodeQL, Dependabot, a release branch, protected main, and documented releases. Phase 0 does not initialize git, publish to GitHub, create issues, create projects, configure branch protection, create tags, or create releases.

## Branching Strategy

- `main`: protected default branch after repository publication.
- `feature/*`: implementation branches for focused changes.
- `release/*`: release preparation branches before tags.
- `hotfix/*`: optional future branch type for urgent corrections.

## Pull Request Strategy

Pull requests should include:

- Purpose.
- Scope.
- Security impact.
- Test evidence.
- Any migration impact.
- Documentation updates.

PRs should require CI passing before merge after a later branch-protection setup is complete.

## CI Strategy

Phase 11 added local GitHub Actions workflow configuration. Hosted Actions have since run; the latest run still requires a successful Tests job after the Phase 13A local fixes.

Configured workflow behavior:

- Install dependencies.
- Run formatting check.
- Run linting.
- Run tests.
- Enforce coverage threshold.
- Run documentation safety checks.
- Run API smoke commands against local SQLite settings.

## CodeQL Strategy

CodeQL is configured for Python in Phase 11 and is expected to run for the public repository. Hosted verification after the audit fixes is pending until the next pushed run completes. Alerts should be reviewed before release. CodeQL configuration remains scoped to the repository and does not require real credentials.

## Dependabot Strategy

Dependabot should monitor:

- Python package ecosystem.
- GitHub Actions ecosystem.

Dependabot PRs should pass CI and be reviewed before merge.

Dependabot is configured in Phase 11, and GitHub has recognized its pip and GitHub Actions update ecosystems.

## Agile Board Plan

Phase 12 adds local Agile planning materials in `docs/agile/` and a local issue template under `.github/ISSUE_TEMPLATE/`. The repository is published, but live GitHub Issues and a live GitHub Project board remain uncreated.

Planned issue categories:

- Phase work items.
- Security controls.
- Authentication.
- RBAC.
- Incident workflow.
- Audit logging.
- Testing.
- Documentation.
- CI/CD.
- Release preparation.

Planned project statuses:

- Backlog.
- In Progress.
- Review.
- Done.

## Release Strategy

Planned release sequence:

1. Complete implementation phases.
2. Confirm tests and coverage.
3. Complete threat model and API documentation.
4. Configure CI, CodeQL, and Dependabot.
5. Prepare release branch.
6. Review limitations and safety documentation.
7. Merge release branch.
8. Create version tag.
9. Create GitHub release.
10. Configure protected main.

The first planned release is `v0.1.0`, but no tag or release is created in Phase 0.
No tag or release exists after Phase 12. `RELEASE.md` and `docs/release-checklist.md` are local preparation artifacts only.

## Definition of Done

A phase is done when:

- Scope is implemented or documented as planned.
- Tests are added where relevant.
- Security constraints are preserved.
- Documentation is updated.
- CI passes once CI exists.
- No real credentials, tokens, incident data, or evidence files are introduced.
