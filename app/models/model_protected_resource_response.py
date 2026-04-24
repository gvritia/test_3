"""Ответ защищенного ресурса для JWT и RBAC."""

from pydantic import BaseModel, Field


class ProtectedResourceResponse(BaseModel):
    """Показывает, кто получил доступ к защищенному маршруту."""
    message: str = Field(..., examples=["Access granted"])
    username: str = Field(..., examples=["alice"])
    role: str | None = Field(default=None, examples=["admin"])
