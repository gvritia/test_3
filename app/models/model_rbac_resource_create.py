"""Тело запроса на создание RBAC-ресурса."""

from pydantic import BaseModel, Field


class RbacResourceCreate(BaseModel):
    """Используется в POST /api/v1/rbac/resources."""
    title: str = Field(..., min_length=1, max_length=120, examples=["Internal guide"])
    content: str = Field(..., min_length=1, max_length=1000, examples=["Read-only content for the team"])
