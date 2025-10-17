from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, pagination, require_project_role
from app.models.comment import Comment
from app.models.task import Task
from app.schemas.comment import CommentCreate, CommentOut, CommentPage

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: UUID,
    data: CommentCreate,
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    comment = Comment(
        task_id=task_id,
        author_id=data.author_id,
        body=data.body,
        created_at=datetime.now(timezone.utc),
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentOut.model_validate(comment, from_attributes=True)


@router.get("", response_model=CommentPage)
async def list_comments(
    task_id: UUID,
    page: dict = Depends(pagination),
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select

    stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.desc()).limit(page["limit"]).offset(page["offset"])
    result = await db.execute(stmt)
    items = result.scalars().all()
    total = (await db.execute(select(Comment).where(Comment.task_id == task_id))).scalars().unique().count()
    return CommentPage(items=[CommentOut.model_validate(x, from_attributes=True) for x in items], total=total)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    task_id: UUID,
    comment_id: UUID,
    _: Any = Depends(require_project_role),
    db: AsyncSession = Depends(get_db),
):
    comment = await db.get(Comment, comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.delete(comment)
    await db.commit()
    return None
