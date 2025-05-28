import pytest
from app.models.currency import FiatCurrency, CryptoCurrency
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService

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
    assert rate is not None
    assert isinstance(rate, float)
    assert rate > 0

    # Prueba con un mercado inexistente
    rate = await conversion_service.get_conversion_rate("invalid-market")
    assert rate is None

@pytest.mark.asyncio
async def test_find_best_conversion(conversion_service):
    # Prueba una conversión válida
    final_amount, intermediate = await conversion_service.find_best_conversion(
        FiatCurrency.CLP,
        FiatCurrency.PEN,
        1000000  # 1 millón de pesos chilenos
    )
    
    assert final_amount is not None
    assert intermediate is not None
    assert isinstance(final_amount, float)
    assert final_amount > 0
    assert intermediate in [CryptoCurrency.BTC, CryptoCurrency.ETH, CryptoCurrency.LTC, CryptoCurrency.BCH]

    # Prueba con monedas inválidas
    final_amount, intermediate = await conversion_service.find_best_conversion(
        FiatCurrency.CLP,
        FiatCurrency.CLP,  # Misma moneda
        1000000
    )
    assert final_amount is None
    assert intermediate is None 