"""Роуты для задания 7.1 (RBAC)."""

from fastapi import APIRouter, Depends, Path, status

from app.api.responses import internal_error_response, merge_responses, validation_error_response
from app.models.model_error_response import ErrorResponse
from app.models.model_message_response import MessageResponse
from app.models.model_protected_resource_response import ProtectedResourceResponse
from app.models.model_rbac_resource_create import RbacResourceCreate
from app.models.model_rbac_resource_response import RbacResourceResponse
from app.models.model_rbac_resource_update import RbacResourceUpdate
from app.models.model_rbac_user_create import RbacUserCreate
from app.models.model_token_response import TokenResponse
from app.models.model_user_credentials import UserCredentials
from app.services.service_rbac import (
    create_rbac_resource,
    delete_rbac_resource,
    get_rbac_resource,
    get_current_rbac_user,
    login_rbac_user,
    register_rbac_user,
    require_roles,
    update_rbac_resource,
)

router = APIRouter(prefix="/api/v1/rbac", tags=["7.1 RBAC"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": MessageResponse, "description": "Пользователь и роль успешно созданы."},
            409: {"model": ErrorResponse, "description": "Пользователь уже существует."},
        },
    ),
    summary="Регистрация пользователя с ролью",
)
async def register_rbac(payload: RbacUserCreate) -> MessageResponse:
    """Регистрирует пользователя вместе с его ролью."""
    register_rbac_user(payload)
    return MessageResponse(message="RBAC user created")


@router.post(
    "/login",
    response_model=TokenResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            200: {"model": TokenResponse, "description": "JWT-токен с ролью успешно выдан."},
            401: {"model": ErrorResponse, "description": "Неверный пароль."},
            404: {"model": ErrorResponse, "description": "Пользователь не найден."},
        },
    ),
    summary="Вход пользователя RBAC",
)
async def login_rbac(payload: UserCredentials) -> TokenResponse:
    """Логин в RBAC-сценарии: на выходе JWT, внутри которого уже есть роль."""
    token = login_rbac_user(payload.username, payload.password)
    return TokenResponse(access_token=token)


@router.get(
    "/protected-resource",
    response_model=ProtectedResourceResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": ProtectedResourceResponse, "description": "Ресурс доступен для admin и user."},
            401: {"model": ErrorResponse, "description": "Токен отсутствует, просрочен или недействителен."},
            403: {"model": ErrorResponse, "description": "Роль пользователя не имеет доступа."},
        },
    ),
    summary="Защищенный ресурс с ограничением ролей",
)
async def get_protected_resource(
    current_user: dict[str, str] = Depends(require_roles("admin", "user")),
) -> ProtectedResourceResponse:
    """Разрешает доступ только ролям admin и user."""
    return ProtectedResourceResponse(
        message="Access granted",
        username=current_user["username"],
        role=current_user["role"],
    )


@router.post(
    "/resources",
    status_code=status.HTTP_201_CREATED,
    response_model=RbacResourceResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            201: {"model": RbacResourceResponse, "description": "Ресурс успешно создан администратором."},
            401: {"model": ErrorResponse, "description": "Токен отсутствует, просрочен или недействителен."},
            403: {"model": ErrorResponse, "description": "Создание ресурса разрешено только admin."},
        },
    ),
    summary="Создать ресурс RBAC",
)
async def create_resource(
    payload: RbacResourceCreate,
    _: dict[str, str] = Depends(require_roles("admin")),
) -> RbacResourceResponse:
    """Создание ресурса разрешено только администратору."""
    return create_rbac_resource(payload)


@router.get(
    "/resources/{resource_id}",
    response_model=RbacResourceResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": RbacResourceResponse, "description": "Ресурс найден."},
            401: {"model": ErrorResponse, "description": "Токен отсутствует, просрочен или недействителен."},
            404: {"model": ErrorResponse, "description": "Ресурс не найден."},
        },
    ),
    summary="Прочитать ресурс RBAC",
)
async def read_resource(
    resource_id: int = Path(..., ge=1),
    _: dict[str, str] = Depends(get_current_rbac_user),
) -> RbacResourceResponse:
    """Чтение разрешено любому аутентифицированному пользователю."""
    return get_rbac_resource(resource_id)


@router.put(
    "/resources/{resource_id}",
    response_model=RbacResourceResponse,
    responses=merge_responses(
        validation_error_response(),
        internal_error_response(),
        {
            200: {"model": RbacResourceResponse, "description": "Ресурс успешно обновлен."},
            401: {"model": ErrorResponse, "description": "Токен отсутствует, просрочен или недействителен."},
            403: {"model": ErrorResponse, "description": "Обновление доступно только admin и user."},
            404: {"model": ErrorResponse, "description": "Ресурс не найден."},
        },
    ),
    summary="Обновить ресурс RBAC",
)
async def update_resource(
    payload: RbacResourceUpdate,
    resource_id: int = Path(..., ge=1),
    _: dict[str, str] = Depends(require_roles("admin", "user")),
) -> RbacResourceResponse:
    """Обновление разрешено ролям admin и user."""
    return update_rbac_resource(resource_id, payload)


@router.delete(
    "/resources/{resource_id}",
    response_model=MessageResponse,
    responses=merge_responses(
        internal_error_response(),
        {
            200: {"model": MessageResponse, "description": "Ресурс успешно удален."},
            401: {"model": ErrorResponse, "description": "Токен отсутствует, просрочен или недействителен."},
            403: {"model": ErrorResponse, "description": "Удаление доступно только admin."},
            404: {"model": ErrorResponse, "description": "Ресурс не найден."},
        },
    ),
    summary="Удалить ресурс RBAC",
)
async def remove_resource(
    resource_id: int = Path(..., ge=1),
    _: dict[str, str] = Depends(require_roles("admin")),
) -> MessageResponse:
    """Удаление разрешено только admin."""
    delete_rbac_resource(resource_id)
    return MessageResponse(message="Resource deleted")
