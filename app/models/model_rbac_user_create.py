"""Модель регистрации пользователя с ролью для задания 7.1."""

from typing import Literal

from pydantic import Field

from app.models.model_user_credentials import UserCredentials


class RbacUserCreate(UserCredentials):
    """Расширяет обычные учетные данные полем role."""
    role: Literal["admin", "user", "guest"] = Field(
        ...,
        description="Роль пользователя в системе RBAC.",
        examples=["user"],
    )
