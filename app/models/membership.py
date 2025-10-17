from __future__ import annotations

from enum import Enum
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MembershipRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class Membership(Base):
    __table_args__ = (
        CheckConstraint("role in ('owner','admin','member','viewer')", name="ck_membership_role"),
    )

    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("project.id"), primary_key=True)
    role: Mapped[str] = mapped_column(Text, default=MembershipRole.member.value)

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="memberships")
