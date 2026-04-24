"""Ответ успешного Basic Auth логина."""

from pydantic import BaseModel, Field


class BasicAuthSecretResponse(BaseModel):
    """Возвращает приветствие и условный секрет из задания 6.2."""
    message: str = Field(..., examples=["Welcome, alice!"])
    secret: str = Field(..., examples=["You got my secret, welcome"])
