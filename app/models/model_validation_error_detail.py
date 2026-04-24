"""Структура одного элемента ошибки валидации FastAPI/Pydantic."""

from typing import Any

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    """Описывает одну проблему во входных данных."""
    type: str = Field(..., examples=["string_too_short"])
    loc: list[str | int] = Field(..., examples=[["body", "username"]])
    msg: str = Field(..., examples=["String should have at least 3 characters"])
    input: Any | None = None
