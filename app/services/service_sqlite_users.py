"""Регистрация пользователей в SQLite для задания 8.1."""

from __future__ import annotations

import sqlite3

from fastapi import HTTPException, status

from app.database import get_db_connection
from app.models.model_sqlite_user_create import SqliteUserCreate


def register_sqlite_user(payload: SqliteUserCreate) -> None:
    """Вставляет новую запись в таблицу users."""
    connection = get_db_connection()
    try:
        connection.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (payload.username, payload.password),
        )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        # UNIQUE на username приводит сюда, если логин уже занят.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from exc
    finally:
        connection.close()
