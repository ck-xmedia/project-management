from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.v1 import auth as r_auth
from app.api.routers.v1 import users as r_users
from app.api.routers.v1 import projects as r_projects
from app.api.routers.v1 import memberships as r_memberships
from app.api.routers.v1 import tasks as r_tasks
from app.api.routers.v1 import comments as r_comments
from app.api.routers.v1 import tags as r_tags
from app.api.routers.v1 import sprints as r_sprints
from app.api.routers.v1 import attachments as r_attachments
from app.api.routers.v1 import activity as r_activity
from app.api import websocket as ws
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title="Project Management API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    api = FastAPI(openapi_url="/openapi.json")
    router = FastAPI()

    app.include_router(r_auth.router, prefix="/api/v1")
    app.include_router(r_users.router, prefix="/api/v1")
    app.include_router(r_projects.router, prefix="/api/v1")
    app.include_router(r_memberships.router, prefix="/api/v1")
    app.include_router(r_tasks.router, prefix="/api/v1")
    app.include_router(r_comments.router, prefix="/api/v1")
    app.include_router(r_tags.router, prefix="/api/v1")
    app.include_router(r_sprints.router, prefix="/api/v1")
    app.include_router(r_attachments.router, prefix="/api/v1")
    app.include_router(r_activity.router, prefix="/api/v1")

    app.include_router(ws.router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.env}

    return app


app = create_app()
