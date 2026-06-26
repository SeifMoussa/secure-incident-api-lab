from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"


def test_contributing_docs_cover_defensive_policy_and_quality_commands() -> None:
    text = CONTRIBUTING.read_text(encoding="utf-8").lower()

    assert CONTRIBUTING.is_file()
    for phrase in [
        "defensive-only policy",
        "offensive tooling",
        "exploit code",
        "malware behavior",
        "real credentials",
        "real access tokens",
        "synthetic/demo data",
        "main",
        "feature/<short-name>",
        "release/<version>",
        "python scripts/check-docs.py",
        "python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95",
    ]:
        assert phrase in text
