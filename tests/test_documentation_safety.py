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
CURRENT_STATUS_PATHS = [
    ROOT / "README.md",
    ROOT / "RELEASE.md",
    ROOT / "docs" / "ci-cd.md",
    ROOT / "docs" / "release-checklist.md",
    ROOT / "docs" / "agile" / "README.md",
    ROOT / "docs" / "agile" / "backlog.md",
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


def test_docs_reflect_phase_13b_without_claiming_pending_release_work_complete() -> None:
    text = combined_docs_text().lower()

    forbidden_claims = [
        "live github projects exist",
        "live github project board exists",
        "dependabot prs were merged",
    ]
    for claim in forbidden_claims:
        assert claim not in text

    current_status = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in CURRENT_STATUS_PATHS
    )
    assert "repository publishing complete" in current_status
    assert "hosted ci passed" in current_status
    assert "hosted codeql passed" in current_status
    assert "open code-scanning alerts: 0" in current_status
    assert "open secret-scanning alerts: 0" in current_status
    assert "live f1-f14 github issues" in current_status
    assert "branch protection configured and verified" in current_status
    assert (
        "project board creation is pending because the token lacks project scope" in current_status
    )
    assert "dependabot prs remain open and unmerged" in current_status
    assert "`v0.1.0` tag exists" in current_status
    assert "github release is published" in current_status
    assert "repository publishing pending" not in current_status
    assert "repository is not published" not in current_status
