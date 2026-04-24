"""Роуты для заданий 6.4 и 6.5.

Файл содержит:
- регистрацию пользователя по JSON;
- логин с выдачей JWT;
- защищенный ресурс, требующий Bearer-токен.
"""

from fastapi import APIRouter, Depends, status

from app.api.responses import internal_error_response, merge_responses, validation_error_response
from app.core.rate_limiter import InMemoryRateLimiter
from app.models.model_error_response import ErrorResponse
from app.models.model_message_response import MessageResponse
from app.models.model_protected_resource_response import ProtectedResourceResponse
from app.models.model_token_response import TokenResponse
from app.models.model_user_credentials import UserCredentials
from app.services.service_jwt_auth import get_current_jwt_user, login_jwt_user, register_jwt_user

router = APIRouter(prefix="/api/v1/jwt-auth", tags=["6.4-6.5 JWT Auth"])
register_rate_limiter = InMemoryRateLimiter(max_requests=1, period_seconds=60)
login_rate_limiter = InMemoryRateLimiter(max_requests=5, period_seconds=60)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": MessageResponse, "description": "Пользователь успешно зарегистрирован."},
            409: {"model": ErrorResponse, "description": "Пользователь уже существует."},
            429: {"model": ErrorResponse, "description": "Превышен лимит запросов на регистрацию."},
        },
    ),
    summary="Регистрация пользователя для JWT",
)
async def register_jwt_auth(
    payload: UserCredentials,
    _: None = Depends(register_rate_limiter),
) -> MessageResponse:
    """Регистрация пользователя с ограничением 1 запрос в минуту."""
    register_jwt_user(payload)
    return MessageResponse(message="New user created")


@router.post(
    "/login",
    response_model=TokenResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            200: {"model": TokenResponse, "description": "JWT-токен успешно выдан."},
            401: {"model": ErrorResponse, "description": "Неверный пароль."},
            404: {"model": ErrorResponse, "description": "Пользователь не найден."},
            429: {"model": ErrorResponse, "description": "Превышен лимит попыток входа."},
        },
    ),
    summary="Вход по JWT",
)
async def login_jwt_auth(
    payload: UserCredentials,
    _: None = Depends(login_rate_limiter),
) -> TokenResponse:
    """Аутентифицирует пользователя и возвращает access_token."""
    token = login_jwt_user(payload)
    return TokenResponse(access_token=token)


@router.get(
    "/protected-resource",
    response_model=ProtectedResourceResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": ProtectedResourceResponse, "description": "Доступ к защищенному ресурсу разрешен."},
            401: {
                "model": ErrorResponse,
                "description": "Токен отсутствует, просрочен или недействителен.",
                "headers": {"WWW-Authenticate": {"description": "Bearer challenge", "schema": {"type": "string"}}},
            },
        },
    ),
    summary="Защищенный ресурс с JWT",
)
async def get_jwt_protected_resource(
    username: str = Depends(get_current_jwt_user),
) -> ProtectedResourceResponse:
    """Пример защищенного эндпоинта из задания 6.4."""
    return ProtectedResourceResponse(message="Access granted", username=username)
