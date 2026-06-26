from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEQL_WORKFLOW = ROOT / ".github" / "workflows" / "codeql.yml"


def test_codeql_workflow_exists_and_has_expected_triggers() -> None:
    text = CODEQL_WORKFLOW.read_text(encoding="utf-8")

    assert CODEQL_WORKFLOW.is_file()
    assert "name: CodeQL" in text
    assert "push:" in text
    assert "pull_request:" in text
    assert "schedule:" in text
    assert "cron:" in text
    assert "workflow_dispatch:" in text


def test_codeql_workflow_configures_python_analysis() -> None:
    text = CODEQL_WORKFLOW.read_text(encoding="utf-8")

    assert "name: CodeQL (python)" in text
    assert "github/codeql-action/init" in text
    assert "github/codeql-action/analyze" in text
    assert "languages: python" in text
    assert "queries: security-and-quality" in text
