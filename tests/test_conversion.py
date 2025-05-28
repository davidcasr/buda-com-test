import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.models.currency import FiatCurrency, CryptoCurrency
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService
from app.exceptions.currency_exceptions import (
    CurrencyNotFoundError,
    ConversionError,
    InvalidAmountError,
    SameCurrencyError,
    BudaAPIError
)
from app.core.circuit_breaker import buda_breaker

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
async def test_cache_behavior(conversion_service):
    # Primera llamada
    rate1 = await conversion_service.get_conversion_rate("btc-clp")
    
    # Segunda llamada (debería usar caché)
    rate2 = await conversion_service.get_conversion_rate("btc-clp")
    
    assert rate1 == rate2

@pytest.mark.asyncio
async def test_circuit_breaker():
    # Simular fallos para activar el circuit breaker
    with patch('httpx.AsyncClient.get', side_effect=Exception("API Error")):
        service = BudaService()
        
        # Intentar varias llamadas para activar el circuit breaker
        for _ in range(5):
            with pytest.raises(Exception):
                await service.get_market_ticker("btc-clp")
        
        # Verificar que el circuit breaker está abierto
        assert buda_breaker.current_state == "open"
        
        await service.close()

@pytest.mark.asyncio
async def test_timeout_handling():
    # Simular un timeout
    with patch('httpx.AsyncClient.get', side_effect=asyncio.TimeoutError()):
        service = BudaService()
        
        with pytest.raises(BudaAPIError) as exc_info:
            await service.get_market_ticker("btc-clp")
        
        assert "Timeout" in str(exc_info.value)
        
        await service.close()

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