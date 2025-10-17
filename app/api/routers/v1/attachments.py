from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_project_role
from app.models.attachment import Attachment
from app.models.task import Task
from app.schemas.attachment import AttachmentOut

router = APIRouter(prefix="/tasks/{task_id}/attachments", tags=["attachments"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("", response_model=AttachmentOut)
async def upload_attachment(
    task_id: UUID,
    file: UploadFile = File(...),
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    # Ensure task exists
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    fname = f"{task_id}-{int(datetime.now(tz=timezone.utc).timestamp())}-{file.filename}"
    dest = UPLOAD_DIR / fname
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)

    att = Attachment(
        task_id=task_id,
        uploader_id=task.reporter_id,
        filename=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        storage_url=f"/uploads/{fname}",
        created_at=datetime.now(timezone.utc),
    )
    db.add(att)
    await db.commit()
    await db.refresh(att)
    return AttachmentOut.model_validate(att, from_attributes=True)
