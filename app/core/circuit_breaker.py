import pybreaker
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class BudaCircuitBreaker(pybreaker.CircuitBreaker):
    """Circuit breaker específico para la API de Buda."""
    def __init__(self):
        super().__init__(
            fail_max=5,  # Número máximo de fallos antes de abrir el circuito
            reset_timeout=60,  # Tiempo en segundos antes de intentar cerrar el circuito
            exclude=[ValueError, TypeError]  # Excepciones que no cuentan como fallos
        )

# Instancia global del circuit breaker
buda_breaker = BudaCircuitBreaker()

def circuit_breaker(func: Callable) -> Callable:
    """
    Decorador para aplicar el circuit breaker a funciones asíncronas.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await buda_breaker(func)(*args, **kwargs)
        except pybreaker.CircuitBreakerError as e:
            logger.error(f"Circuit breaker abierto: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error en la llamada: {str(e)}")
            raise

    return wrapper 