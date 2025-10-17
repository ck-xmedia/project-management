from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class MembershipCreate(BaseModel):
    user_id: UUID
    role: Role


class MembershipUpdate(BaseModel):
    role: Role


class MembershipOut(BaseModel):
    user_id: UUID
    project_id: UUID
    role: str
