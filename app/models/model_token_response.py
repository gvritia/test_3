"""Ответ с JWT access token."""

from typing import Literal

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Стандартное тело ответа при успешной JWT-аутентификации."""
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: Literal["bearer"] = "bearer"
