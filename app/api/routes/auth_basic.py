"""Роуты для заданий 6.1 и 6.2.

Здесь находятся:
- POST /register с JSON-телом;
- GET /login с Basic Auth.
"""

from fastapi import APIRouter, Depends, status

from app.api.responses import internal_error_response, merge_responses, validation_error_response
from app.models.model_basic_auth_secret_response import BasicAuthSecretResponse
from app.models.model_error_response import ErrorResponse
from app.models.model_message_response import MessageResponse
from app.models.model_user_credentials import UserCredentials
from app.models.model_user_in_db import UserInDB
from app.services.service_basic_auth import authenticate_basic_auth_user, register_basic_auth_user

router = APIRouter(prefix="/api/v1/basic-auth", tags=["6.1-6.2 Basic Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": MessageResponse, "description": "Пользователь успешно зарегистрирован."},
            409: {"model": ErrorResponse, "description": "Пользователь с таким username уже существует."},
        },
    ),
    summary="Регистрация пользователя для Basic Auth",
)
async def register_basic_auth(payload: UserCredentials) -> MessageResponse:
    """Создает пользователя для сценария Basic Auth."""
    register_basic_auth_user(payload)
    return MessageResponse(message="User successfully added")


@router.get(
    "/login",
    response_model=BasicAuthSecretResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            200: {"model": BasicAuthSecretResponse, "description": "Успешная Basic-аутентификация."},
            401: {
                "model": ErrorResponse,
                "description": "Учетные данные не переданы или неверны.",
                "headers": {"WWW-Authenticate": {"description": "Basic challenge", "schema": {"type": "string"}}},
            },
        },
    ),
    summary="Вход по Basic Auth",
)
async def login_basic_auth(
    current_user: UserInDB = Depends(authenticate_basic_auth_user),
) -> BasicAuthSecretResponse:
    """Пускает только после успешной проверки через dependency auth."""
    return BasicAuthSecretResponse(
        message=f"Welcome, {current_user.username}!",
        secret="You got my secret, welcome",
    )
