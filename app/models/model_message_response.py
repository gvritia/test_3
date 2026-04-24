"""Модель ответа с простым текстовым сообщением."""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Универсальный успешный ответ вида {"message": "..."}."""
    message: str = Field(..., examples=["New user created"])
