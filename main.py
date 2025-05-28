import logging
from fastapi import FastAPI
from app.core.config import settings
from app.middleware.error_handler import error_handler_middleware
from app.routers import health, conversion
from app.core.dependencies import cleanup_services

# Configuración de logging usando settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI con configuración desde settings
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Agregar middleware de manejo de errores
app.middleware("http")(error_handler_middleware)

# Incluir routers
app.include_router(health.router)
app.include_router(conversion.router)

@app.on_event("startup")
async def startup_event():
    """
    Eventos de inicio de la aplicación.
    """
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Configuración: Buda API URL = {settings.buda_api_url}")
    logger.info(f"Configuración: Request timeout = {settings.request_timeout}s")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cierra las conexiones al cerrar la aplicación.
    """
    logger.info("Cerrando aplicación...")
    await cleanup_services()
    logger.info("Aplicación cerrada correctamente") 