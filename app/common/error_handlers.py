"""Central safe error handlers."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def add_error_handlers(app: FastAPI) -> None:
    """Register safe JSON error handlers that do not echo request bodies."""

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "Request validation failed."},
        )
