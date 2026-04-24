"""Модель полного обновления Todo через PUT."""

from pydantic import Field

from app.models.model_todo_base import TodoBase


class TodoUpdate(TodoBase):
    """Для обновления клиент присылает уже все поля, включая completed."""
    completed: bool = Field(..., description="Статус выполнения задачи.", examples=[False])
