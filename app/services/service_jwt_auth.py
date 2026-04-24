"""Бизнес-логика для заданий 6.4 и 6.5.

Файл отвечает за:
- регистрацию пользователя для JWT-сценария;
- вход и выдачу токена;
- извлечение текущего пользователя из Bearer-токена.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status

from app.core.security import create_access_token, decode_access_token, extract_bearer_token, hash_password, verify_password
from app.models.model_user_credentials import UserCredentials
from app.models.model_user_in_db import UserInDB

jwt_users_db: dict[str, UserInDB] = {}


def _find_username(username: str) -> str | None:
    """Ищет пользователя в памяти с защитой от timing attack."""
    for stored_username in jwt_users_db:
        if secrets.compare_digest(stored_username.encode("utf-8"), username.encode("utf-8")):
            return stored_username
    return None


def register_jwt_user(payload: UserCredentials) -> None:
    """Создает нового JWT-пользователя и сохраняет bcrypt-хеш пароля."""
    if _find_username(payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    jwt_users_db[payload.username] = UserInDB(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )


def login_jwt_user(payload: UserCredentials) -> str:
    """Проверяет учетные данные и возвращает готовый JWT."""
    stored_username = _find_username(payload.username)
    if stored_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stored_user = jwt_users_db[stored_username]
    if not verify_password(payload.password, stored_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    return create_access_token({"sub": stored_user.username})


def get_current_jwt_user(token: str = Depends(extract_bearer_token)) -> str:
    """Достает username из JWT claim sub."""
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(username)
