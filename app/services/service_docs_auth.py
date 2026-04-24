"""Проверка доступа к Swagger/OpenAPI для задания 6.3."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials

from app.core.config import settings
from app.core.security import extract_basic_credentials


def verify_docs_access(
    credentials: HTTPBasicCredentials = Depends(extract_basic_credentials),
) -> None:
    """Разрешает доступ к документации только по учетным данным из .env."""
    valid_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.docs_user.encode("utf-8"),
    )
    valid_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.docs_password.encode("utf-8"),
    )

    if not valid_username or not valid_password:
        # WWW-Authenticate нужен, чтобы клиент понимал,
        # что требуется Basic-аутентификация.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
