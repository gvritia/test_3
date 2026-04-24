"""Базовая модель Todo для задания 8.2."""

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Общие поля title и description для create/update."""
    title: str = Field(..., min_length=1, max_length=120, examples=["Buy groceries"])
    description: str = Field(..., min_length=1, max_length=500, examples=["Milk, eggs, bread"])
