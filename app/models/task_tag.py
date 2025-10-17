from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskTag(Base):
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_tasktag_project_name"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    name: Mapped[str]


class TaskTagLink(Base):
    task_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("task.id"), primary_key=True)
    tag_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tasktag.id"), primary_key=True)
