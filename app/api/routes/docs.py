"""Переопределение Swagger/OpenAPI для задания 6.3."""

from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from app.services.service_docs_auth import verify_docs_access


def build_docs_router(app: FastAPI) -> APIRouter:
    """Создает router с защищенными /docs и /openapi.json."""
    router = APIRouter(tags=["6.3 Protected Docs"])

    @router.get("/docs", include_in_schema=False, summary="Swagger UI")
    async def docs(_: None = Depends(verify_docs_access)):
        # include_in_schema=False скрывает маршрут из самой OpenAPI-схемы.
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

    @router.get("/openapi.json", include_in_schema=False, summary="OpenAPI schema")
    async def openapi_schema(_: None = Depends(verify_docs_access)):
        # Возвращаем схему вручную, чтобы тоже защитить ее Basic Auth.
        return JSONResponse(app.openapi())

    return router
