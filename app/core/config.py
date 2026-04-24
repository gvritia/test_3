"""Конфигурация приложения.

Основное назначение:
- задание 6.3: режимы DEV/PROD и защита документации;
- задания 6.4-7.1: SECRET_KEY и время жизни JWT;
- задания 8.1-8.2: путь к SQLite-базе.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Объект с уже прочитанными и проверенными настройками приложения."""

    mode: str
    docs_user: str
    docs_password: str
    secret_key: str
    jwt_expire_minutes: int
    database_path: Path


def load_settings() -> Settings:
    """Читает переменные окружения и валидирует их до запуска FastAPI."""

    mode = os.getenv("MODE", "DEV").upper()
    if mode not in {"DEV", "PROD"}:
        # Если режим указан неверно, лучше остановить запуск сразу,
        # чем получить непредсказуемое поведение на этапе работы.
        raise ValueError("MODE must be either DEV or PROD")

    database_path = Path(os.getenv("DATABASE_PATH", "app.db")).resolve()

    # Возвращаем один готовый объект, чтобы не читать env-файл по всему проекту.
    return Settings(
        mode=mode,
        docs_user=os.getenv("DOCS_USER", "admin"),
        docs_password=os.getenv("DOCS_PASSWORD", "secret"),
        secret_key=os.getenv("SECRET_KEY", "change-me-please-32-characters-min"),
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "30")),
        database_path=database_path,
    )


# Глобальный объект настроек импортируется в других модулях.
settings = load_settings()
