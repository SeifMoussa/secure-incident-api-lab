from pathlib import Path

from fastapi.testclient import TestClient

TEST_PASSWORD = "SyntheticSafety!123"


def test_auth_responses_do_not_contain_sensitive_values(client: TestClient, test_settings) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "safety@example.com",
            "password": TEST_PASSWORD,
            "display_name": "Synthetic Safety User",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "safety@example.com", "password": TEST_PASSWORD},
    )

    combined_response_text = register_response.text + login_response.text
    assert "password_hash" not in combined_response_text
    assert TEST_PASSWORD not in combined_response_text
    assert test_settings.jwt_secret_key not in combined_response_text


def test_docs_do_not_contain_raw_auth_examples() -> None:
    root = Path(__file__).resolve().parents[1]
    docs_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [root / "README.md", *sorted((root / "docs").glob("*.md"))]
    )

    assert "SyntheticSafety!123" not in docs_text
    assert "Bearer ey" not in docs_text
    assert "synthetic-test-secret-for-phase-3-only" not in docs_text


def test_no_rbac_admin_domain_ci_or_git_work_started() -> None:
    root = Path(__file__).resolve().parents[1]
    forbidden_paths = [
        "app/api/routes/users.py",
        "app/api/routes/incidents.py",
        "app/api/routes/tickets.py",
        "app/api/routes/evidence.py",
        "app/api/routes/remediation.py",
        "app/api/routes/audit.py",
        "app/rbac",
        "app/security_headers.py",
        ".git/HEAD",
    ]

    for relative_path in forbidden_paths:
        assert not (root / relative_path).exists(), relative_path
