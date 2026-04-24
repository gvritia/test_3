"""RBAC-логика для задания 7.1.

Здесь строится надстройка над JWT:
- пользователь получает роль;
- роль кладется в токен;
- доступ к ресурсам ограничивается через dependency require_roles.
"""

from __future__ import annotations

import secrets
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.core.security import create_access_token, decode_access_token, extract_bearer_token, hash_password, verify_password
from app.models.model_rbac_resource_create import RbacResourceCreate
from app.models.model_rbac_resource_response import RbacResourceResponse
from app.models.model_rbac_resource_update import RbacResourceUpdate
from app.models.model_rbac_user_create import RbacUserCreate

rbac_users_db: dict[str, dict[str, str]] = {}
rbac_resources_db: dict[int, RbacResourceResponse] = {}
rbac_resource_sequence = 0


def _find_username(username: str) -> str | None:
    """Ищет пользователя по безопасному сравнению имени."""
    for stored_username in rbac_users_db:
        if secrets.compare_digest(stored_username.encode("utf-8"), username.encode("utf-8")):
            return stored_username
    return None


def register_rbac_user(payload: RbacUserCreate) -> None:
    """Создает пользователя и сразу назначает ему роль."""
    if _find_username(payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    rbac_users_db[payload.username] = {
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
    }


def login_rbac_user(username: str, password: str) -> str:
    """Выдает JWT, в который дополнительно записывается role."""
    stored_username = _find_username(username)
    if stored_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stored_user = rbac_users_db[stored_username]
    if not verify_password(password, stored_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    return create_access_token(
        {
            "sub": stored_username,
            "role": stored_user["role"],
        }
    )


def get_current_rbac_user(token: str = Depends(extract_bearer_token)) -> dict[str, str]:
    """Извлекает из JWT и пользователя, и его роль."""
    payload = decode_access_token(token)
    username = payload.get("sub")
    role = payload.get("role")

    if not username or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "username": str(username),
        "role": str(role),
    }


def require_roles(*allowed_roles: str) -> Callable[[dict[str, str]], dict[str, str]]:
    """Фабрика dependency, которая пропускает только указанные роли."""

    def dependency(current_user: dict[str, str] = Depends(get_current_rbac_user)) -> dict[str, str]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this role",
            )
        return current_user

    return dependency


def create_rbac_resource(payload: RbacResourceCreate) -> RbacResourceResponse:
    """Создает ресурс, с которым потом работают роли admin/user/guest."""
    global rbac_resource_sequence
    rbac_resource_sequence += 1
    resource = RbacResourceResponse(
        id=rbac_resource_sequence,
        title=payload.title,
        content=payload.content,
    )
    rbac_resources_db[resource.id] = resource
    return resource


def get_rbac_resource(resource_id: int) -> RbacResourceResponse:
    """Возвращает ресурс по id или 404, если ресурс не найден."""
    resource = rbac_resources_db.get(resource_id)
    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )
    return resource


def update_rbac_resource(resource_id: int, payload: RbacResourceUpdate) -> RbacResourceResponse:
    """Полностью обновляет ресурс."""
    resource = get_rbac_resource(resource_id)
    updated_resource = RbacResourceResponse(
        id=resource.id,
        title=payload.title,
        content=payload.content,
    )
    rbac_resources_db[resource_id] = updated_resource
    return updated_resource


def delete_rbac_resource(resource_id: int) -> None:
    """Удаляет ресурс из in-memory хранилища."""
    get_rbac_resource(resource_id)
    del rbac_resources_db[resource_id]
