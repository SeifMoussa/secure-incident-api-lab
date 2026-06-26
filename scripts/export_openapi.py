"""Export the FastAPI OpenAPI schema without starting a server."""

import json
from pathlib import Path

from app.config import Settings
from app.main import create_app


def export_openapi() -> Path:
    """Write a deterministic local OpenAPI JSON document."""
    settings = Settings(
        environment="test",
        debug=False,
        rate_limit_enabled=False,
    )
    app = create_app(settings)
    output_path = Path("docs") / "openapi.json"
    output_path.write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


if __name__ == "__main__":
    path = export_openapi()
    print(f"Exported OpenAPI schema to {path}")
