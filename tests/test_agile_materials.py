from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGILE = ROOT / "docs" / "agile"


def test_agile_materials_exist_with_expected_board_plan() -> None:
    readme = AGILE / "README.md"
    backlog = AGILE / "backlog.md"
    board = AGILE / "board-plan.md"
    template = ROOT / ".github" / "ISSUE_TEMPLATE" / "feature.md"

    assert readme.is_file()
    assert backlog.is_file()
    assert board.is_file()
    assert template.is_file()

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [readme, backlog, board, template]
    ).lower()

    for column in ["backlog", "in progress", "review", "done"]:
        assert column in combined
    for label in [
        "auth",
        "rbac",
        "incident",
        "ticket",
        "evidence",
        "remediation",
        "audit",
        "security",
        "validation",
        "test",
        "docs",
        "ci",
        "release",
    ]:
        assert label in combined


def test_agile_backlog_documents_f1_through_f14() -> None:
    text = (AGILE / "backlog.md").read_text(encoding="utf-8")

    for number in range(1, 15):
        assert f"## F{number}:" in text
    for phrase in ["Scope:", "Acceptance criteria:", "Status:"]:
        assert phrase in text


def test_agile_materials_reflect_live_issues_and_no_fake_screenshot_exists() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in AGILE.glob("*.md")).lower()

    assert "live f1-f14 github issues" in combined
    assert "f1-f13 are closed" in combined
    assert "f14 remains open" in combined
    assert "github project #1" in combined
    assert "f14 is `in progress`" in combined
    assert "real board screenshot" in combined
    assert (
        "no fake screenshot" in combined or "do not add placeholder or fake screenshots" in combined
    )
    assert not (AGILE / "board_sprint1.png").exists()
