from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates

from interface.routers import auth_api
from settings import get_settings
from utils.logger import get_logger

config = get_settings()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация настроек до запуска сервиса"""
    logger.info(app)
    yield


app = FastAPI(
    title=config.project_name,
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description=config.project_description,
    version=config.project_version,
    lifespan=lifespan,
    debug=config.is_debug_mode,
)
app.include_router(auth_api)
