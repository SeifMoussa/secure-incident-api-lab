from pathlib import Path

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_phase_files_exist() -> None:
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


def test_no_accidental_domain_admin_or_ci_implementation() -> None:
    forbidden_paths = [
        "app/db",
        "app/models",
        "app/rbac",
        "app/api/routes/incidents.py",
        "app/api/routes/tickets.py",
        "app/api/routes/evidence.py",
        "app/api/routes/remediation.py",
        "app/api/routes/audit.py",
    ]

    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path


def test_only_phase_3_routes_are_registered(test_settings) -> None:
    app = create_app(test_settings)
    route_paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/" in route_paths
    assert "/health" in route_paths
    assert "/auth/register" in route_paths
    assert "/auth/login" in route_paths
    assert "/auth/refresh" in route_paths
    assert "/auth/logout" in route_paths
    assert "/auth/me" in route_paths
    assert "/incidents/" in route_paths
    assert "/audit/" in route_paths


def test_env_example_contains_placeholders_only() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    lower_content = env_example.lower()

    assert "CHANGE_ME_FOR_LOCAL_DEVELOPMENT" in env_example
    assert "sk-" not in env_example
    assert "ghp_" not in env_example
    assert "github_pat_" not in env_example
    assert "postgresql://" not in lower_content
    assert "password=" not in lower_content
