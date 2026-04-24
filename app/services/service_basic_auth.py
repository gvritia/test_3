"""Бизнес-логика для заданий 6.1 и 6.2.

Здесь хранится in-memory база пользователей для Basic Auth,
регистрация и аутентификация пользователя.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials

from app.core.security import extract_basic_credentials, hash_password, verify_password
from app.models.model_user_credentials import UserCredentials
from app.models.model_user_in_db import UserInDB

# Учебная in-memory "база".
basic_auth_users_db: dict[str, UserInDB] = {}


def _find_username(username: str) -> str | None:
    """Ищет пользователя безопасным сравнением строк через compare_digest."""
    for stored_username in basic_auth_users_db:
        if secrets.compare_digest(stored_username.encode("utf-8"), username.encode("utf-8")):
            return stored_username
    return None


def register_basic_auth_user(payload: UserCredentials) -> None:
    """Регистрирует пользователя и сохраняет только хеш пароля."""
    existing_username = _find_username(payload.username)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    basic_auth_users_db[payload.username] = UserInDB(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )


def authenticate_basic_auth_user(
    credentials: HTTPBasicCredentials = Depends(extract_basic_credentials),
) -> UserInDB:
    """Проверяет логин/пароль и возвращает объект пользователя из in-memory БД."""
    stored_username = _find_username(credentials.username)
    if stored_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    stored_user = basic_auth_users_db[stored_username]
    # Пароль сверяется не напрямую, а через bcrypt-хеш.
    if not verify_password(credentials.password, stored_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return stored_user
