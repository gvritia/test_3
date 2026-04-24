"""Модель входных учетных данных пользователя."""

from pydantic import Field, field_validator

from app.models.model_user_base import UserBase


class UserCredentials(UserBase):
    """Используется там, где клиент присылает логин и пароль в JSON."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль пользователя. Минимум 8 символов, должен содержать буквы и цифры.",
        examples=["qwerty123"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Проверяет, что пароль содержит и буквы, и цифры."""
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        if not has_letter or not has_digit:
            raise ValueError("Password must contain at least one letter and one digit")
        return value
