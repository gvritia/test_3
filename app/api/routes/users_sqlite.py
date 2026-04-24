"""Роуты для задания 8.1: сохранение пользователя в SQLite."""

from fastapi import APIRouter, status

from app.api.responses import internal_error_response, merge_responses, validation_error_response
from app.models.model_error_response import ErrorResponse
from app.models.model_message_response import MessageResponse
from app.models.model_sqlite_user_create import SqliteUserCreate
from app.services.service_sqlite_users import register_sqlite_user

router = APIRouter(prefix="/api/v1/sqlite-users", tags=["8.1 SQLite Users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": MessageResponse, "description": "Пользователь успешно добавлен в таблицу users."},
            409: {"model": ErrorResponse, "description": "Пользователь с таким username уже существует."},
        },
    ),
    summary="Регистрация пользователя в SQLite",
)
async def register_user_sqlite(payload: SqliteUserCreate) -> MessageResponse:
    """Создает пользователя в таблице users."""
    register_sqlite_user(payload)
    return MessageResponse(message="User registered successfully!")
