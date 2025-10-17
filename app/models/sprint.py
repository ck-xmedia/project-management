from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sprint(Base):
    __table_args__ = (
        CheckConstraint("state in ('planned','active','completed')", name="ck_sprint_state"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("project.id"))
    name: Mapped[str] = mapped_column(Text)
    start_date: Mapped[date | None]
    end_date: Mapped[date | None]
    state: Mapped[str] = mapped_column(Text, default="planned")

    project = relationship("Project", back_populates="sprints")
