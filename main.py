from fastapi import FastAPI, Request
from app.models.currency import ConversionRequest, ConversionResponse
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService
from app.middleware.error_handler import error_handler_middleware
from app.exceptions.currency_exceptions import CurrencyValidationError
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Conversión de Monedas",
    description="API para convertir monedas fiat usando criptomonedas como intermediarias",
    version="1.0.0"
)

# Agregar middleware de manejo de errores
app.middleware("http")(error_handler_middleware)

# Inicialización de servicios
buda_service = BudaService()
conversion_service = ConversionService(buda_service)

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API.
    """
    return {"status": "OK"}

@app.get("/convert", response_model=ConversionResponse)
async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float
):
    """
    Convierte un monto de una moneda fiat a otra usando criptomonedas como intermediarias.
    """
    try:
        request = ConversionRequest(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount
        )
    except ValueError as e:
        raise CurrencyValidationError(
            "Error de validación en los parámetros de entrada",
            {"error": str(e)}
        )

    final_amount, intermediate_currency = await conversion_service.find_best_conversion(
        request.from_currency,
        request.to_currency,
        request.amount
    )

    return ConversionResponse(
        final_amount=final_amount,
        intermediate_currency=intermediate_currency,
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        original_amount=request.amount
    )

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cierra las conexiones al cerrar la aplicación.
    """
    await buda_service.close() 