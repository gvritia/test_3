"""Модель стандартной ошибки API."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Используется в responses для описания тела ошибок."""
    detail: str = Field(..., examples=["Authorization failed"])
