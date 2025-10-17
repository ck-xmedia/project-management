from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __table_args__ = (
        CheckConstraint("status in ('todo','in_progress','blocked','done')", name="ck_task_status"),
        CheckConstraint("priority in ('low','medium','high','urgent')", name="ck_task_priority"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("project.id"))
    sprint_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sprint.id"), nullable=True)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("task.id"), nullable=True)

    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[str] = mapped_column(Text, default="todo")
    priority: Mapped[str] = mapped_column(Text, default="medium")
    assignee_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    reporter_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("user.id"))
    estimate: Mapped[int | None]
    due_date: Mapped[date | None]

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
