from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        payload: Dict[str, Any] = {
            "type": "about:blank",
            "title": exc.detail or "Error",
            "status": exc.status_code,
            "detail": exc.detail,
        }
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://example.com/validation-error",
                "title": "Validation Error",
                "status": 422,
                "errors": exc.errors(),
            },
        )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        response = await call_next(request)
        return response
