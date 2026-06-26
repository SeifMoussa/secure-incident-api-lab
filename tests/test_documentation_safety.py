import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "PROJECT_COMPLETION_CHECKLIST.md",
    ROOT / "RELEASE.md",
    *sorted((ROOT / "docs").glob("*.md")),
    *sorted((ROOT / "docs" / "agile").glob("*.md")),
]

JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
API_KEY_PATTERN = re.compile(r"\b(?:sk|pk|rk|ghp|github_pat)_[A-Za-z0-9_]{12,}")
DB_PASSWORD_PATTERN = re.compile(r"://[^/\s:]+:[^@\s]+@")
BEARER_VALUE_PATTERN = re.compile(r"Authorization:\s*Bearer\s+(?!<ACCESS_TOKEN>)[^\s<]+", re.I)


def combined_docs_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in DOC_PATHS)


def test_docs_do_not_include_real_looking_tokens_keys_or_database_passwords() -> None:
    text = combined_docs_text()

    assert JWT_PATTERN.search(text) is None
    assert API_KEY_PATTERN.search(text) is None
    assert DB_PASSWORD_PATTERN.search(text) is None
    assert BEARER_VALUE_PATTERN.search(text) is None


def test_docs_use_placeholders_in_examples() -> None:
    text = (ROOT / "docs" / "api_reference.md").read_text(encoding="utf-8")

    for placeholder in [
        "<ACCESS_TOKEN>",
        "<REFRESH_TOKEN>",
        "<USER_ID>",
        "<INCIDENT_ID>",
        "<PASSWORD_PLACEHOLDER>",
    ]:
        assert placeholder in text


def test_docs_do_not_claim_ci_publishing_release_or_branch_protection_complete() -> None:
    text = combined_docs_text().lower()

    forbidden_claims = [
        "ci has passed",
        "github actions passed",
        "repository is currently published",
        "release is available",
        "release has been created",
        "v0.1.0 release exists",
        "branch protection is currently configured",
        "branch protection exists",
        "codeql is enabled",
        "live github issues exist",
        "live github projects exist",
    ]
    for claim in forbidden_claims:
        assert claim not in text
    assert (
        "ci, git initialization, github publishing, tags, releases, "
        "and branch protection remain unimplemented"
    ) in text
