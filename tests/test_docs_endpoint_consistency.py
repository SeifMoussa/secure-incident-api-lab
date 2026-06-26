from app.config import Settings
from app.main import create_app


def normalized_path(path: str) -> str:
    return path.replace("{uid}", "{uid}")


def implemented_http_routes() -> set[str]:
    app = create_app(Settings(environment="test", rate_limit_enabled=False))
    routes: set[str] = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        if path in {"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}:
            continue
        for method in sorted(methods):
            if method in {"HEAD", "OPTIONS"}:
                continue
            routes.add(f"{method} {normalized_path(path)}")
    return routes


def documented_routes() -> set[str]:
    with open("docs/api_reference.md", encoding="utf-8") as api_reference:
        text = api_reference.read()
    routes: set[str] = set()
    for line in text.splitlines():
        if line.startswith("### "):
            _, method, path = line.split(maxsplit=2)
            routes.add(f"{method} {path}")
    return routes


def test_api_reference_matches_implemented_routes() -> None:
    assert documented_routes() == implemented_http_routes()
