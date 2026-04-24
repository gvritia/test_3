"""Модель регистрации пользователя в SQLite для задания 8.1."""

from pydantic import BaseModel, Field


class SqliteUserCreate(BaseModel):
    """Входные данные для POST /api/v1/sqlite-users/register."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
        examples=["test_user"],
    )
    password: str = Field(
        ...,
        min_length=5,
        max_length=128,
        description="По условию 8.1 пароль хранится в открытом виде, но проходит базовую валидацию длины.",
        examples=["12345"],
    )
