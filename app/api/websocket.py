from __future__ import annotations

from typing import DefaultDict, Dict, List
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: DefaultDict[UUID, List[WebSocket]] = DefaultDict(list)

    async def connect(self, project_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self.active[project_id].append(ws)

    def remove(self, project_id: UUID, ws: WebSocket) -> None:
        if ws in self.active[project_id]:
            self.active[project_id].remove(ws)

    async def broadcast(self, project_id: UUID, message: Dict) -> None:
        for ws in list(self.active[project_id]):
            try:
                await ws.send_json(message)
            except Exception:
                self.remove(project_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/projects/{project_id}")
async def ws_projects(ws: WebSocket, project_id: UUID):
    await manager.connect(project_id, ws)
    try:
        while True:
            await ws.receive_text()  # keepalive or ignore
    except WebSocketDisconnect:
        manager.remove(project_id, ws)
