import pytest
import asyncio
from typing import AsyncGenerator
from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService

@pytest.fixture(scope="session")
def event_loop():
    """Crear un event loop para los tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def buda_service() -> AsyncGenerator[BudaService, None]:
    """Fixture para el servicio de Buda."""
    service = BudaService()
    yield service
    await service.close()

@pytest.fixture
async def conversion_service(buda_service: BudaService) -> ConversionService:
    """Fixture para el servicio de conversión."""
    return ConversionService(buda_service) 