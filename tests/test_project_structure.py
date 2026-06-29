from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_core_project_files_exist() -> None:
    expected_paths = [
        "pyproject.toml",
        ".gitignore",
        ".env.example",
        "LICENSE",
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/common/__init__.py",
        "app/common/health.py",
        "app/auth/router.py",
        "app/auth/service.py",
        "app/auth/schemas.py",
        "app/auth/utils.py",
        "app/auth/password_policy.py",
        "app/auth/dependencies.py",
        "app/auth/common_passwords.txt",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_health.py",
        "tests/test_config.py",
        "tests/test_project_structure.py",
        "alembic.ini",
        "alembic/env.py",
        "alembic/versions/20260625_0001_create_initial_tables.py",
    ]

    for relative_path in expected_paths:
        assert (ROOT / relative_path).is_file(), relative_path


def test_env_example_contains_placeholders_only() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    lower_content = env_example.lower()

    assert "CHANGE_ME_FOR_LOCAL_DEVELOPMENT" in env_example
    assert "sk-" not in env_example
    assert "ghp_" not in env_example
    assert "github_pat_" not in env_example
    assert "postgresql://" not in lower_content
    assert "password=" not in lower_content
