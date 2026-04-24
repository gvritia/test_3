"""Общие шаблоны ответов OpenAPI.

Файл не относится к одному конкретному заданию.
Он нужен, чтобы не дублировать описания статусов 422 и 500 во всех роутерах.
Это реализация принципа DRY.
"""

from __future__ import annotations

from app.models.model_error_response import ErrorResponse
from app.models.model_validation_error_response import ValidationErrorResponse


def validation_error_response() -> dict[int, dict]:
    """Шаблон ответа для ошибок валидации Pydantic/FastAPI."""
    return {
        422: {
            "model": ValidationErrorResponse,
            "description": "Ошибка валидации входных данных.",
        }
    }


def internal_error_response() -> dict[int, dict]:
    """Шаблон ответа на случай непредвиденной серверной ошибки."""
    return {
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера.",
        }
    }


def merge_responses(*response_sets: dict[int, dict]) -> dict[int, dict]:
    """Объединяет несколько словарей responses в один."""
    merged: dict[int, dict] = {}
    for response_set in response_sets:
        merged.update(response_set)
    return merged
