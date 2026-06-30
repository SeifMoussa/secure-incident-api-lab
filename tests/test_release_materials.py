from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_materials_exist_and_document_current_repository_status() -> None:
    release = ROOT / "RELEASE.md"
    checklist = ROOT / "docs" / "release-checklist.md"

    release_text = release.read_text(encoding="utf-8").lower()
    checklist_text = checklist.read_text(encoding="utf-8").lower()

    assert release.is_file()
    assert checklist.is_file()
    for phrase in [
        "v0.1.0 - secure incident management api",
        "hosted checks",
        "repository status",
        "suggested github topics",
        "linkedin post draft",
        "cv bullets",
        "recruiter-facing summary",
    ]:
        assert phrase in release_text
    for status in [
        "- [x] git initialization complete.",
        "- [x] repository publishing complete.",
        "- [x] public repository visibility confirmed.",
        "- [x] hosted ci passed at the latest phase 13b commit.",
        "- [x] hosted codeql passed at the latest phase 13b commit.",
        "- [x] github issues f1-f14 created and left open.",
        "- [x] branch protection configured and verified for `main`.",
        "- [ ] project board creation pending because the token lacks project scope.",
        "- [x] `v0.1.0` tag exists.",
        "- [x] github release is published.",
    ]:
        assert status in checklist_text


def test_release_materials_do_not_claim_pending_release_or_project_work_done() -> None:
    text = (
        (ROOT / "RELEASE.md").read_text(encoding="utf-8")
        + "\n"
        + (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
    ).lower()

    for forbidden in [
        "github projects have been created",
        "dependabot prs were merged",
    ]:
        assert forbidden not in text
