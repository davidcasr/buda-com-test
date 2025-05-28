from fastapi import APIRouter, Depends
from decimal import Decimal
from app.models.requests import ConversionRequest
from app.models.responses import ConversionResponse
from app.services.conversion_service import ConversionService
from app.exceptions.currency_exceptions import CurrencyValidationError
from app.core.dependencies import get_conversion_service

router = APIRouter(tags=["Conversion"])

@router.get("/convert", response_model=ConversionResponse)
async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float,
    conversion_service: ConversionService = Depends(get_conversion_service)
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
