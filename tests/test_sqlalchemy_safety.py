import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1] / "app"


def iter_app_python_files():
    yield from APP_ROOT.rglob("*.py")


def test_app_source_does_not_use_raw_sql_text_constructs() -> None:
    offenders: list[str] = []
    for path in iter_app_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "text"
            ):
                offenders.append(str(path.relative_to(APP_ROOT.parent)))

    assert offenders == []


def test_app_source_does_not_build_sql_with_f_strings_or_string_concatenation() -> None:
    offenders: list[str] = []
    sql_words = ("select ", "insert ", "update ", "delete ", " from ", " where ")
    for path in iter_app_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                text = "".join(
                    part.value.lower() for part in node.values if isinstance(part, ast.Constant)
                )
                if any(word in text for word in sql_words):
                    offenders.append(str(path.relative_to(APP_ROOT.parent)))
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                left = getattr(node.left, "value", "")
                right = getattr(node.right, "value", "")
                combined = f"{left} {right}".lower()
                if any(word in combined for word in sql_words):
                    offenders.append(str(path.relative_to(APP_ROOT.parent)))

    assert offenders == []


def test_tests_use_local_sqlite_only_for_database_fixtures() -> None:
    conftest = (APP_ROOT.parent / "tests" / "conftest.py").read_text(encoding="utf-8")

    assert "sqlite+pysqlite:///:memory:" in conftest
    assert "postgresql://" not in conftest.lower()
    assert "mysql://" not in conftest.lower()
