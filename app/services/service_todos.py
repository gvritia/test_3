"""CRUD-операции для Todo из задания 8.2."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.database import get_db_connection
from app.models.model_todo_create import TodoCreate
from app.models.model_todo_response import TodoResponse
from app.models.model_todo_update import TodoUpdate


def create_todo(payload: TodoCreate) -> TodoResponse:
    """Создает запись в БД и возвращает уже сохраненный объект."""
    connection = get_db_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (payload.title, payload.description, 0),
        )
        connection.commit()
        todo_id = int(cursor.lastrowid)
    finally:
        connection.close()

    return get_todo(todo_id)


def get_todo(todo_id: int) -> TodoResponse:
    """Читает один Todo по его id."""
    connection = get_db_connection()
    try:
        row = connection.execute(
            "SELECT id, title, description, completed FROM todos WHERE id = ?",
            (todo_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return TodoResponse(
        id=int(row["id"]),
        title=str(row["title"]),
        description=str(row["description"]),
        completed=bool(row["completed"]),
    )


def update_todo(todo_id: int, payload: TodoUpdate) -> TodoResponse:
    """Полностью обновляет Todo по id."""
    connection = get_db_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE todos
            SET title = ?, description = ?, completed = ?
            WHERE id = ?
            """,
            (payload.title, payload.description, int(payload.completed), todo_id),
        )
        connection.commit()
    finally:
        connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return get_todo(todo_id)


def delete_todo(todo_id: int) -> None:
    """Удаляет Todo по id."""
    connection = get_db_connection()
    try:
        cursor = connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        connection.commit()
    finally:
        connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
