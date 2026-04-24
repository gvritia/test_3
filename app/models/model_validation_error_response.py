"""Полное тело ответа 422 для невалидного запроса."""

from pydantic import BaseModel, Field

from app.models.model_validation_error_detail import ValidationErrorDetail


class ValidationErrorResponse(BaseModel):
    """Список всех найденных ошибок валидации."""
    detail: list[ValidationErrorDetail] = Field(default_factory=list)
