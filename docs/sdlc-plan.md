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

Branch protection now requires pull requests, one approving review, an up-to-date branch, and successful Tests, Docs Safety Checks, API Smoke, and CodeQL (python) checks before merge.

## CI Strategy

Phase 11 added local GitHub Actions workflow configuration. Hosted Actions passed all three CI jobs at the latest Phase 13B commit.

Configured workflow behavior:

- Install dependencies.
- Run formatting check.
- Run linting.
- Run tests.
- Enforce coverage threshold.
- Run documentation safety checks.
- Run API smoke commands against local SQLite settings.

## CodeQL Strategy

CodeQL is configured for Python and passed at the latest Phase 13B commit. Open code-scanning alerts and open secret-scanning alerts are both 0. CodeQL configuration remains scoped to the repository and does not require real credentials.

## Dependabot Strategy

Dependabot should monitor:

- Python package ecosystem.
- GitHub Actions ecosystem.

Dependabot PRs should pass CI and be reviewed before merge.

Dependabot is configured in Phase 11, and GitHub has recognized its pip and GitHub Actions update ecosystems. PRs #1-#4 were reviewed individually in Phase 14 and remain open and unmerged because they cross major/version boundaries and their current Tests checks fail.

## Agile Board Plan

Phase 12 added local Agile planning materials in `docs/agile/` and a local issue template under `.github/ISSUE_TEMPLATE/`. Phase 13B created live F1-F14 Issues and the planned labels. Phase 14 closed F1-F13 as completed, kept F14 open, and created GitHub Project #1 with F1-F13 in `Done` and F14 in `In Progress`. A real board screenshot remains pending.

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

The first release is `v0.1.0`. Its annotated tag and GitHub Release were published in Phase 13C after hosted CI and CodeQL passed. `RELEASE.md` and `docs/release-checklist.md` record the verified release state.

## Definition of Done

A phase is done when:

- Scope is implemented or documented as planned.
- Tests are added where relevant.
- Security constraints are preserved.
- Documentation is updated.
- CI passes once CI exists.
- No real credentials, tokens, incident data, or evidence files are introduced.
