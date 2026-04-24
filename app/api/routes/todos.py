"""Роуты CRUD для задания 8.2."""

from fastapi import APIRouter, Path, status

from app.api.responses import internal_error_response, merge_responses, validation_error_response
from app.models.model_error_response import ErrorResponse
from app.models.model_message_response import MessageResponse
from app.models.model_todo_create import TodoCreate
from app.models.model_todo_response import TodoResponse
from app.models.model_todo_update import TodoUpdate
from app.services.service_todos import create_todo, delete_todo, get_todo, update_todo

router = APIRouter(prefix="/api/v1/todos", tags=["8.2 Todos"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TodoResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": TodoResponse, "description": "Todo успешно создан."},
        },
    ),
    summary="Создать новый Todo",
)
async def create_todo_endpoint(payload: TodoCreate) -> TodoResponse:
    """Создает новый Todo через POST."""
    return create_todo(payload)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": TodoResponse, "description": "Todo найден."},
            404: {"model": ErrorResponse, "description": "Todo с указанным id не найден."},
        },
    ),
    summary="Получить Todo по id",
)
async def get_todo_endpoint(todo_id: int = Path(..., ge=1)) -> TodoResponse:
    """Читает один Todo по id через GET."""
    return get_todo(todo_id)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            200: {"model": TodoResponse, "description": "Todo успешно обновлен."},
            404: {"model": ErrorResponse, "description": "Todo с указанным id не найден."},
        },
    ),
    summary="Обновить Todo по id",
)
async def update_todo_endpoint(
    payload: TodoUpdate,
    todo_id: int = Path(..., ge=1),
) -> TodoResponse:
    """Полностью обновляет Todo через PUT."""
    return update_todo(todo_id, payload)


@router.delete(
    "/{todo_id}",
    response_model=MessageResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": MessageResponse, "description": "Todo успешно удален."},
            404: {"model": ErrorResponse, "description": "Todo с указанным id не найден."},
        },
    ),
    summary="Удалить Todo по id",
)
async def delete_todo_endpoint(todo_id: int = Path(..., ge=1)) -> MessageResponse:
    """Удаляет Todo по id через DELETE."""
    delete_todo(todo_id)
    return MessageResponse(message="Todo deleted successfully")
