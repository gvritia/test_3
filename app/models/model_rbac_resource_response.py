"""Модель ответа для ресурса RBAC."""

from pydantic import BaseModel, Field


class RbacResourceResponse(BaseModel):
    """То, что возвращается клиенту после CRUD-операций с ресурсом."""
    id: int = Field(..., ge=1, examples=[1])
    title: str = Field(..., examples=["Internal guide"])
    content: str = Field(..., examples=["Read-only content for the team"])
