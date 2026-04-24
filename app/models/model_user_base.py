"""Базовая пользовательская модель для заданий 6.x и 7.1."""

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Содержит общий набор полей пользователя."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
        description="Логин пользователя. Допускаются только латинские буквы, цифры и underscore.",
        examples=["alice_01"],
    )
