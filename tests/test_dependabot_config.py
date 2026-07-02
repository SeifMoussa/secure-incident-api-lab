from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPENDABOT_CONFIG = ROOT / ".github" / "dependabot.yml"


def test_dependabot_config_exists_and_covers_expected_ecosystems() -> None:
    text = DEPENDABOT_CONFIG.read_text(encoding="utf-8")

    assert DEPENDABOT_CONFIG.is_file()
    assert "version: 2" in text
    assert "package-ecosystem: pip" in text
    assert "package-ecosystem: github-actions" in text
    assert text.count("interval: weekly") == 2


def test_dependabot_config_has_no_unrelated_ecosystems() -> None:
    text = DEPENDABOT_CONFIG.read_text(encoding="utf-8")

    for ecosystem in ["docker", "npm", "gomod", "cargo", "maven"]:
        assert f"package-ecosystem: {ecosystem}" not in text


def test_dependabot_ignores_incompatible_bcrypt_major_updates() -> None:
    text = DEPENDABOT_CONFIG.read_text(encoding="utf-8")

    assert "dependency-name: bcrypt" in text
    assert "version-update:semver-major" in text
