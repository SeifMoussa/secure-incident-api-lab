from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_workflow_files_are_present() -> None:
    assert (ROOT / ".github" / "workflows" / "ci.yml").is_file()
    assert (ROOT / ".github" / "workflows" / "codeql.yml").is_file()
    assert (ROOT / ".github" / "dependabot.yml").is_file()


def test_workflows_do_not_claim_hosted_success_or_publish() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in [
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / ".github" / "workflows" / "codeql.yml",
            ROOT / ".github" / "dependabot.yml",
        ]
    )

    for forbidden in [
        "gh release",
        "git push",
        "branches: [release",
        "hosted ci passed",
        "hosted codeql passed",
        "branch protection",
    ]:
        assert forbidden not in combined
