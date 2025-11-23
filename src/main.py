from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.common.di_container import di
from src.config import settings
from src.controller.routing.auth import auth_router
from src.integration.db_connection_provider import PGConnectionProvider
from src.service.generic.auth_middleware import JWTAuthMiddleware
from src.service.generic.logger import logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    di.register_pg(PGConnectionProvider)
    yield
    await di.pg_connection_provider.close_connection_pool()
    di.unregister_resources()


app = FastAPI(title="Avito trainee assignment: Сервис назначения ревьюеров для Pull Request’ов", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if settings.AUTH_ENABLED:
    logger.info("Authorization Enabled")
    app.add_middleware(JWTAuthMiddleware)
    app.include_router(auth_router)


@app.get("/", include_in_schema=False)
def redirect_to_redoc() -> RedirectResponse:
    """Redirect to ReDoc"""
    return RedirectResponse(url="/redoc", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}
