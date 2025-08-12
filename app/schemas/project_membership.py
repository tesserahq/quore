from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProjectMembershipBase(BaseModel):
    user_id: UUID
    project_id: UUID
    role: str
    created_by_id: UUID


class ProjectMembershipCreate(ProjectMembershipBase):
    pass


class ProjectMembershipUpdate(BaseModel):
    role: Optional[str] = None


class ProjectMembershipInDB(ProjectMembershipBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
