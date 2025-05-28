import asyncio
import logging
from typing import Dict, Tuple
from app.services.buda_service import BudaService
from app.exceptions.currency_exceptions import BudaAPIError

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, buda_service: BudaService):
        self.buda_service = buda_service
    
    async def check_liveness(self) -> bool:
        """
        Verifica si la aplicación está viva (liveness probe).
        Este check debe ser muy simple y rápido.
        """
        return True
    
    async def check_readiness(self) -> Tuple[bool, Dict[str, str], int, int]:
        """
        Verifica si la aplicación está lista para recibir tráfico (readiness probe).
        Retorna: (is_ready, dependencies_status, checks_passed, checks_total)
        """
        dependencies = {}
        checks_passed = 0
        checks_total = 0
        
        # Check 1: Buda API connectivity
        checks_total += 1
        buda_status = await self._check_buda_api()
        dependencies["buda_api"] = buda_status
        if buda_status == "healthy":
            checks_passed += 1
        
        # Check 2: Cache functionality (simple check)
        checks_total += 1
        cache_status = await self._check_cache()
        dependencies["cache"] = cache_status
        if cache_status == "healthy":
            checks_passed += 1
        
        # Determinar si está ready
        is_ready = checks_passed == checks_total
        
        return is_ready, dependencies, checks_passed, checks_total
    
    async def _check_buda_api(self) -> str:
        """
        Verifica la conectividad con la API de Buda.
        """
        try:
            # Timeout más corto para health checks
            await asyncio.wait_for(
                self.buda_service.get_available_markets(),
                timeout=5.0
            )
            return "healthy"
        except asyncio.TimeoutError:
            logger.warning("Buda API health check timeout")
            return "timeout"
        except BudaAPIError as e:
            logger.warning(f"Buda API health check failed: {e}")
            return "unhealthy"
        except Exception as e:
            logger.error(f"Unexpected error in Buda API health check: {e}")
            return "error"
    
    async def _check_cache(self) -> str:
        """
        Verifica que el sistema de caché funcione correctamente.
        """
        try:
            # Test básico de cache - esto es un placeholder
            # En una implementación real, podrías verificar Redis, Memcached, etc.
            return "healthy"
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return "unhealthy"
    
    async def get_detailed_status(self) -> Dict:
        """
        Obtiene un estado detallado del sistema para debugging.
        """
        is_ready, dependencies, checks_passed, checks_total = await self.check_readiness()
        
        return {
            "application": {
                "status": "healthy" if await self.check_liveness() else "unhealthy",
                "ready": is_ready
            },
            "dependencies": dependencies,
            "checks": {
                "passed": checks_passed,
                "total": checks_total,
                "success_rate": f"{(checks_passed/checks_total)*100:.1f}%" if checks_total > 0 else "0%"
            }
        } 