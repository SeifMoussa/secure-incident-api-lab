from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THREAT_MODEL = ROOT / "docs" / "threat_model.md"


def test_threat_model_exists_and_covers_stride_categories() -> None:
    text = THREAT_MODEL.read_text(encoding="utf-8").lower()

    assert THREAT_MODEL.is_file()
    for category in [
        "spoofing",
        "tampering",
        "repudiation",
        "information disclosure",
        "denial of service",
        "elevation of privilege",
    ]:
        assert category in text


def test_threat_model_documents_assets_boundaries_and_limitations() -> None:
    text = THREAT_MODEL.read_text(encoding="utf-8").lower()

    for asset in [
        "user credentials",
        "password hashes",
        "access tokens",
        "refresh-token jtis",
        "incident data",
        "ticket data",
        "evidence notes",
        "attachment metadata",
        "remediation tasks",
        "audit logs",
        "admin role-management capability",
        "api configuration and secrets",
    ]:
        assert asset in text
    for boundary in [
        "client to api",
        "api to database",
        "authenticated user to protected endpoints",
        "admin to user-management endpoints",
        "auditor to audit logs",
        "local/dev/test environment boundaries",
    ]:
        assert boundary in text
    assert "not a deployed production soc platform" in text
    assert "residual risks and limitations" in text


def test_threat_model_documents_key_mitigations() -> None:
    text = THREAT_MODEL.read_text(encoding="utf-8").lower()

    for mitigation in [
        "jwt validation",
        "rbac",
        "audit logging",
        "strict pydantic schemas",
        "rate-limited",
        "security middleware",
        "cors uses an explicit allowlist",
        "sqlalchemy orm",
        "sanitizer recursively redacts",
        "production settings disable",
    ]:
        assert mitigation in text
