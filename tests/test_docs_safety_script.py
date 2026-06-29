import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-docs.py"


def load_check_docs_module():
    spec = importlib.util.spec_from_file_location("check_docs_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_docs_safety_script_exists_and_passes_locally() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check-docs.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert SCRIPT.is_file()
    assert result.returncode == 0
    assert "Documentation safety checks passed." in result.stdout


def test_docs_safety_script_rejects_unsafe_content() -> None:
    module = load_check_docs_module()

    with pytest.raises(SystemExit):
        module.check_sensitive_patterns('{"access_token":"eyJaaaa.bbbbbbbb.cccccccc"}')
    with pytest.raises(SystemExit):
        module.check_forbidden_claims("Hosted CI has passed.")
    with pytest.raises(SystemExit):
        module.check_current_status("Repository publishing pending.")

    module.check_forbidden_claims("The repository is published publicly.")


def test_docs_safety_script_checks_required_files() -> None:
    module = load_check_docs_module()

    docs = module.read_required_files(module.REQUIRED_DOCS)
    workflows = module.read_required_files(module.REQUIRED_WORKFLOWS)

    assert "README.md" in docs
    assert "RELEASE.md" in docs
    assert "CONTRIBUTING.md" in docs
    assert "docs/agile/backlog.md" in docs
    assert "docs/release-checklist.md" in docs
    assert ".github/workflows/ci.yml" in workflows
