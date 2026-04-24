"""Модель создания Todo.

При создании completed не передается клиентом и по умолчанию становится False в БД.
"""

from app.models.model_todo_base import TodoBase


class TodoCreate(TodoBase):
    """POST-модель для создания Todo."""
    pass
