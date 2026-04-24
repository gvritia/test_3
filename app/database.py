"""Работа с SQLite.

Файл относится к заданиям 8.1 и 8.2:
- создает соединение с БД;
- поднимает таблицы users и todos.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

from app.core.config import settings


def get_db_connection() -> sqlite3.Connection:
    """Открывает соединение с SQLite и включает доступ к колонкам по имени."""
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Создает таблицы, если их еще нет в базе."""
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        # Таблица users требуется для задания 8.1.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
        # Таблица todos требуется для задания 8.2.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.commit()
