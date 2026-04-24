"""Модель пользователя в хранилище.

Относится к заданию 6.2, где по условию нельзя хранить открытый пароль.
"""

from pydantic import Field

from app.models.model_user_base import UserBase


class UserInDB(UserBase):
    """Хранит логин и уже захешированный пароль."""
    hashed_password: str = Field(..., min_length=20)
