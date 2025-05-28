from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from decimal import Decimal
import logging

# Importaciones de configuración y modelos
from app.core.config import settings
from app.models.requests import ConversionRequest
from app.models.responses import ConversionResponse, HealthResponse, ReadinessResponse, ErrorResponse

# Importaciones de servicios
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService
from app.services.health_service import HealthService

# Importaciones de middleware y excepciones
from app.middleware.error_handler import error_handler_middleware
from app.exceptions.currency_exceptions import CurrencyValidationError

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

# Inicialización de servicios
buda_service = BudaService()
conversion_service = ConversionService(buda_service)
health_service = HealthService(buda_service)

# ================================
# HEALTH CHECK ENDPOINTS
# ================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Endpoint básico de health check.
    Retorna el estado general de la aplicación.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )

@app.get("/health/live", response_model=HealthResponse, tags=["Health"])
async def liveness_check():
    """
    Liveness probe - verifica si la aplicación está viva.
    Usado por Kubernetes para determinar si reiniciar el pod.
    """
    is_alive = await health_service.check_liveness()
    status = "healthy" if is_alive else "unhealthy"
    
    if not is_alive:
        raise HTTPException(status_code=503, detail="Service not alive")
    
    return HealthResponse(
        status=status,
        version=settings.app_version
    )

@app.get("/health/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness probe - verifica si la aplicación está lista para recibir tráfico.
    Usado por Kubernetes para determinar si enviar tráfico al pod.
    """
    is_ready, dependencies, checks_passed, checks_total = await health_service.check_readiness()
    
    status = "ready" if is_ready else "not_ready"
    
    if not is_ready:
        raise HTTPException(
            status_code=503, 
            detail=ReadinessResponse(
                status=status,
                dependencies=dependencies,
                checks_passed=checks_passed,
                checks_total=checks_total
            ).dict()
        )
    
    return ReadinessResponse(
        status=status,
        dependencies=dependencies,
        checks_passed=checks_passed,
        checks_total=checks_total
    )

# ================================
# CONVERSION ENDPOINTS
# ================================

@app.get("/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float
):
    """
    Convierte un monto de una moneda fiat a otra usando criptomonedas como intermediarias.
    
    - **from_currency**: Moneda de origen (CLP, COP, PEN)
    - **to_currency**: Moneda de destino (CLP, COP, PEN)  
    - **amount**: Monto a convertir (debe ser mayor que 0)
    """
    try:
        # Validar entrada usando el modelo mejorado
        request = ConversionRequest(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=Decimal(str(amount))
        )
    except ValueError as e:
        raise CurrencyValidationError(
            "Error de validación en los parámetros de entrada",
            {"error": str(e)}
        )

    # Realizar conversión
    final_amount, intermediate_currency = await conversion_service.find_best_conversion(
        request.from_currency,
        request.to_currency,
        request.amount
    )

    # Calcular tasa de conversión efectiva
    conversion_rate = final_amount / request.amount if request.amount > 0 else Decimal('0')

    return ConversionResponse(
        final_amount=final_amount,
        intermediate_currency=intermediate_currency.value,
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        original_amount=request.amount,
        conversion_rate=conversion_rate
    )

# ================================
# LIFECYCLE EVENTS
# ================================

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
    await buda_service.close()
    logger.info("Aplicación cerrada correctamente") 