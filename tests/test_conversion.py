import pytest
from app.models.currency import FiatCurrency, CryptoCurrency
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService
from app.exceptions.currency_exceptions import (
    CurrencyNotFoundError,
    ConversionError,
    InvalidAmountError,
    SameCurrencyError
)

@pytest.fixture
async def buda_service():
    service = BudaService()
    yield service
    await service.close()

@pytest.fixture
def conversion_service(buda_service):
    return ConversionService(buda_service)

@pytest.mark.asyncio
async def test_get_conversion_rate(conversion_service):
    # Prueba con un mercado existente
    rate = await conversion_service.get_conversion_rate("btc-clp")
    assert isinstance(rate, float)
    assert rate > 0

    # Prueba con un mercado inexistente
    with pytest.raises(CurrencyNotFoundError) as exc_info:
        await conversion_service.get_conversion_rate("invalid-market")
    assert "No se encontró información de ticker" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_best_conversion(conversion_service):
    # Prueba una conversión válida
    final_amount, intermediate = await conversion_service.find_best_conversion(
        FiatCurrency.CLP,
        FiatCurrency.PEN,
        1000000  # 1 millón de pesos chilenos
    )
    
    assert isinstance(final_amount, float)
    assert final_amount > 0
    assert intermediate in [CryptoCurrency.BTC, CryptoCurrency.ETH, CryptoCurrency.LTC, CryptoCurrency.BCH]

    # Prueba con monedas inválidas (misma moneda)
    with pytest.raises(SameCurrencyError) as exc_info:
        await conversion_service.find_best_conversion(
            FiatCurrency.CLP,
            FiatCurrency.CLP,
            1000000
        )
    assert "No se puede convertir entre la misma moneda" in str(exc_info.value)

    # Prueba con monto inválido
    with pytest.raises(InvalidAmountError) as exc_info:
        await conversion_service.find_best_conversion(
            FiatCurrency.CLP,
            FiatCurrency.PEN,
            -1000
        )
    assert "El monto a convertir debe ser mayor que cero" in str(exc_info.value)

    # Prueba con monto cero
    with pytest.raises(InvalidAmountError) as exc_info:
        await conversion_service.find_best_conversion(
            FiatCurrency.CLP,
            FiatCurrency.PEN,
            0
        )
    assert "El monto a convertir debe ser mayor que cero" in str(exc_info.value)

@pytest.mark.asyncio
async def test_conversion_error_handling(conversion_service):
    # Prueba el manejo de errores en la conversión
    with pytest.raises(ConversionError) as exc_info:
        await conversion_service.find_best_conversion(
            FiatCurrency.CLP,
            FiatCurrency.PEN,
            1000000
        )
    assert "No se encontró una ruta de conversión válida" in str(exc_info.value)
    assert "errors" in exc_info.value.details 