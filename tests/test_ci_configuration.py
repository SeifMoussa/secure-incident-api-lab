from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_workflow_exists_and_has_expected_triggers() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert CI_WORKFLOW.is_file()
    assert "name: CI" in text
    assert "push:" in text
    assert "branches: [main]" in text
    assert "pull_request:" in text
    assert "workflow_dispatch:" in text


def test_ci_workflow_uses_python_311_and_stable_job_names() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert 'python-version: "3.11"' in text
    assert "name: Tests" in text
    assert "name: Docs Safety Checks" in text
    assert "name: API Smoke" in text


def test_ci_workflow_runs_required_quality_commands() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    for command in [
        'python -m pip install -e ".[dev]"',
        "python -m pytest --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=95",
        "python -m ruff check .",
        "python -m ruff format --check .",
        "python scripts/export_openapi.py",
        "python scripts/check-docs.py",
        "python -m py_compile scripts/export_openapi.py",
        "python -m py_compile scripts/check-docs.py",
        "python -m uvicorn app.main:create_app --factory --help",
        "python -m alembic upgrade head",
        "python -m alembic current",
    ]:
        assert command in text


def test_ci_workflow_uses_local_sqlite_and_no_external_services() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8").lower()

    assert "sqlite:///./dev-placeholder.sqlite3" in text
    assert "services:" not in text
    assert "postgres" not in text
    assert "redis" not in text
    assert "docker" not in text
