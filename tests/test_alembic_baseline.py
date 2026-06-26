from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "alembic" / "versions" / "20260625_0001_create_initial_tables.py"


def test_alembic_files_exist() -> None:
    assert (ROOT / "alembic.ini").is_file()
    assert (ROOT / "alembic" / "env.py").is_file()
    assert BASELINE.is_file()


def test_baseline_migration_mentions_expected_tables() -> None:
    migration = BASELINE.read_text(encoding="utf-8")

    for table_name in [
        "users",
        "incidents",
        "tickets",
        "evidence_notes",
        "evidence_attachments",
        "remediation_tasks",
        "audit_log",
        "token_blocklist",
    ]:
        assert f'"{table_name}"' in migration


def test_no_phase_3_or_domain_api_routes_were_added() -> None:
    forbidden_paths = [
        "app/api/routes/auth.py",
        "app/api/routes/users.py",
        "app/api/routes/incidents.py",
        "app/api/routes/tickets.py",
        "app/api/routes/evidence.py",
        "app/api/routes/remediation.py",
        "app/api/routes/audit.py",
    ]

    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path
