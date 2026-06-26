from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_materials_exist_and_document_pending_hosted_work() -> None:
    release = ROOT / "RELEASE.md"
    checklist = ROOT / "docs" / "release-checklist.md"

    release_text = release.read_text(encoding="utf-8").lower()
    checklist_text = checklist.read_text(encoding="utf-8").lower()

    assert release.is_file()
    assert checklist.is_file()
    for phrase in [
        "v0.1.0 - secure incident management api",
        "pending hosted checks",
        "manual git publishing commands",
        "github cli publishing commands",
        "suggested github topics",
        "linkedin post draft",
        "cv bullets",
        "recruiter-facing summary",
    ]:
        assert phrase in release_text
    for pending in [
        "- [ ] git initialization pending.",
        "- [ ] repository publishing pending.",
        "- [ ] hosted ci pending.",
        "- [ ] hosted codeql pending.",
        "- [ ] branch protection pending.",
        "- [ ] `v0.1.0` tag pending.",
        "- [ ] github release pending.",
    ]:
        assert pending in checklist_text


def test_release_materials_do_not_claim_publishing_done() -> None:
    text = (
        (ROOT / "RELEASE.md").read_text(encoding="utf-8")
        + "\n"
        + (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
    ).lower()

    for forbidden in [
        "hosted ci has passed",
        "hosted codeql has passed",
        "repository is currently published",
        "release has been created",
        "branch protection is configured",
        "github issues have been created",
        "github projects have been created",
    ]:
        assert forbidden not in text
