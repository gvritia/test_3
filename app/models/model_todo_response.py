"""Модель ответа с полным представлением Todo."""

from pydantic import BaseModel, Field


class TodoResponse(BaseModel):
    """То, что клиент получает после чтения/создания/обновления Todo."""
    id: int = Field(..., ge=1, examples=[1])
    title: str = Field(..., examples=["Buy groceries"])
    description: str = Field(..., examples=["Milk, eggs, bread"])
    completed: bool = Field(..., examples=[False])
