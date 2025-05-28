from fastapi import FastAPI, HTTPException
from app.models.currency import ConversionRequest, ConversionResponse
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService

app = FastAPI(
    title="API de Conversión de Monedas",
    description="API para convertir monedas fiat usando criptomonedas como intermediarias",
    version="1.0.0"
)

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
        raise HTTPException(status_code=400, detail=str(e))

    final_amount, intermediate_currency = await conversion_service.find_best_conversion(
        request.from_currency,
        request.to_currency,
        request.amount
    )

    if not final_amount or not intermediate_currency:
        raise HTTPException(
            status_code=404,
            detail="No se encontró una ruta de conversión válida"
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