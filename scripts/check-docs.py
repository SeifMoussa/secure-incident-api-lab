"""Validate documentation and workflow safety for local CI configuration."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "PROJECT_COMPLETION_CHECKLIST.md",
    "RELEASE.md",
    "docs/threat_model.md",
    "docs/api_reference.md",
    "docs/openapi.json",
    "docs/ci-cd.md",
    "docs/security-scope.md",
    "docs/testing-plan.md",
    "docs/api-plan.md",
    "docs/architecture.md",
    "docs/release-checklist.md",
    "docs/agile/README.md",
    "docs/agile/backlog.md",
    "docs/agile/board-plan.md",
]

REQUIRED_WORKFLOWS = [
    ".github/workflows/ci.yml",
    ".github/workflows/codeql.yml",
    ".github/dependabot.yml",
]

CURRENT_STATUS_DOCS = [
    "README.md",
    "RELEASE.md",
    "docs/ci-cd.md",
    "docs/release-checklist.md",
    "docs/agile/README.md",
    "docs/agile/backlog.md",
]

REQUIRED_PHRASES = [
    "defensive",
    "synthetic",
    "production-pattern",
    "no real credentials",
    "metadata-only",
    "no binary upload",
    "jwt",
    "rbac",
    "audit logging",
    "rate limiting",
    "security headers",
    "cors allowlist",
    "threat model",
    "api reference",
    "openapi",
]

FORBIDDEN_CLAIMS = [
    "github projects have been created",
    "live github projects exist",
    "live github project board exists",
    "dependabot prs were merged",
    "dependabot prs have been merged",
]

STALE_PUBLICATION_CLAIMS = [
    "repository is not published",
    "repository has not been published",
    "repository publishing pending",
    "pending until publishing",
    "pending future publishing phase",
]

REQUIRED_CURRENT_STATUS = [
    "repository publishing complete",
    "repository is published publicly",
    "hosted ci passed",
    "hosted codeql passed",
    "open code-scanning alerts: 0",
    "open secret-scanning alerts: 0",
    "live f1-f14 github issues",
    "branch protection configured and verified",
    "project board creation is pending because the token lacks project scope",
    "dependabot prs remain open and unmerged",
    "`v0.1.0` tag exists",
    "github release is published",
]

JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
API_KEY_PATTERN = re.compile(r"\b(?:sk|pk|rk|ghp|github_pat)_[A-Za-z0-9_]{12,}")
DB_PASSWORD_PATTERN = re.compile(r"://[^/\s:]+:[^@\s]+@")
BEARER_VALUE_PATTERN = re.compile(r"Authorization:\s*Bearer\s+(?!<ACCESS_TOKEN>)[^\s<]+", re.I)
RAW_PASSWORD_PATTERN = re.compile(r'"password"\s*:\s*"(?!<PASSWORD_PLACEHOLDER>)[^"<][^"]*"', re.I)
CUSTOMER_DATA_PATTERN = re.compile(r"\b(real customer|customer incident|customer data)\b", re.I)


def fail(message: str) -> None:
    raise SystemExit(f"docs safety check failed: {message}")


def read_required_files(paths: list[str]) -> dict[str, str]:
    contents: dict[str, str] = {}
    for relative_path in paths:
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing required file: {relative_path}")
        contents[relative_path] = path.read_text(encoding="utf-8")
    return contents


def check_required_phrases(text: str) -> None:
    lower_text = text.lower()
    for phrase in REQUIRED_PHRASES:
        if phrase not in lower_text:
            fail(f"missing required documentation phrase: {phrase}")


def check_forbidden_claims(text: str) -> None:
    lower_text = text.lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim in lower_text:
            fail(f"forbidden completion claim found: {claim}")


def check_current_status(text: str) -> None:
    lower_text = text.lower()
    for claim in STALE_PUBLICATION_CLAIMS:
        if claim in lower_text:
            fail(f"stale publication claim found: {claim}")
    for phrase in REQUIRED_CURRENT_STATUS:
        if phrase not in lower_text:
            fail(f"missing current repository status: {phrase}")


def check_sensitive_patterns(text: str) -> None:
    checks = [
        (JWT_PATTERN, "real-looking JWT"),
        (API_KEY_PATTERN, "real-looking API key"),
        (DB_PASSWORD_PATTERN, "database password URL"),
        (BEARER_VALUE_PATTERN, "non-placeholder bearer token"),
        (RAW_PASSWORD_PATTERN, "raw password example"),
    ]
    for pattern, label in checks:
        if pattern.search(text):
            fail(f"found {label}")

    allowed_customer_context = (
        "no real",
        "do not use",
        "do not add",
        "not include",
        "out of scope",
        "should be used",
        "without using",
        "- real customer",
    )
    for match in CUSTOMER_DATA_PATTERN.finditer(text):
        start = max(0, match.start() - 100)
        context = text[start : match.end() + 100].lower()
        if not any(allowed in context for allowed in allowed_customer_context):
            fail("possible real customer data claim")


def main() -> int:
    docs = read_required_files(REQUIRED_DOCS)
    read_required_files(REQUIRED_WORKFLOWS)
    combined_docs = "\n".join(docs.values())
    current_status = "\n".join(docs[path] for path in CURRENT_STATUS_DOCS)
    check_required_phrases(combined_docs)
    check_forbidden_claims(combined_docs)
    check_current_status(current_status)
    check_sensitive_patterns(combined_docs)
    print("Documentation safety checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
