from app.services.buda_service import BudaService
from app.services.conversion_service import ConversionService
from app.services.health_service import HealthService

# Servicios singleton
_buda_service = None
_conversion_service = None
_health_service = None

def get_buda_service() -> BudaService:
    """Obtiene la instancia singleton del servicio de Buda."""
    global _buda_service
    if _buda_service is None:
        _buda_service = BudaService()
    return _buda_service

def get_conversion_service() -> ConversionService:
    """Obtiene la instancia singleton del servicio de conversión."""
    global _conversion_service
    if _conversion_service is None:
        _conversion_service = ConversionService(get_buda_service())
    return _conversion_service

def get_health_service() -> HealthService:
    """Obtiene la instancia singleton del servicio de health checks."""
    global _health_service
    if _health_service is None:
        _health_service = HealthService(get_buda_service())
    return _health_service

async def cleanup_services():
    """Limpia los servicios al cerrar la aplicación."""
    global _buda_service
    if _buda_service:
        await _buda_service.close()
