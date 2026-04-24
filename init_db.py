"""Отдельный скрипт инициализации БД для задания 8.1/8.2."""

from app.database import initialize_database


if __name__ == "__main__":
    # Удобно запускать вручную перед проверкой, если нужно создать таблицы заранее.
    initialize_database()
    print("Database initialized successfully.")
