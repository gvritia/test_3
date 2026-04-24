"""Общие функции безопасности.

Файл используется в заданиях:
- 6.2: хеширование и проверка пароля;
- 6.3: извлечение Basic Auth для /docs;
- 6.4-6.5: создание и проверка JWT;
- 7.1: повторное использование JWT для RBAC.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from passlib.context import CryptContext

from app.core.config import settings

# Passlib инкапсулирует алгоритмы хеширования паролей.
# Здесь выбран bcrypt, потому что это стандартный и безопасный вариант
# для учебной задачи и хорошо подходит под требование задания 6.2/6.5.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# auto_error=False позволяет нам самим формировать 401 и нужный WWW-Authenticate.
basic_security = HTTPBasic(auto_error=False)
bearer_security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Преобразует обычный пароль в безопасный хеш."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает пароль из запроса с хешем из хранилища."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict[str, Any], expires_minutes: int | None = None) -> str:
    """Создает JWT с полезной нагрузкой и временем истечения."""

    expiration = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.jwt_expire_minutes,
    )
    # claim exp нужен, чтобы токен автоматически устаревал.
    token_payload = payload | {"exp": expiration}
    return jwt.encode(token_payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    """Декодирует JWT и выбрасывает 401, если токен неверный или просрочен."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def extract_basic_credentials(
    credentials: HTTPBasicCredentials | None = Depends(basic_security),
) -> HTTPBasicCredentials:
    """Достает username/password из Basic Auth заголовка."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


def extract_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_security),
) -> str:
    """Достает Bearer-токен из заголовка Authorization."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
