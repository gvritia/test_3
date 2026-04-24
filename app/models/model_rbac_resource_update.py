"""Тело запроса на обновление RBAC-ресурса."""

from pydantic import BaseModel, Field


class RbacResourceUpdate(BaseModel):
    """Используется в PUT /api/v1/rbac/resources/{id}."""
    title: str = Field(..., min_length=1, max_length=120, examples=["Updated guide"])
    content: str = Field(..., min_length=1, max_length=1000, examples=["Updated content"])
