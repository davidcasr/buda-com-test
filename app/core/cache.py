from aiocache import cached
from aiocache.serializers import PickleSerializer
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

def cache_response(ttl: int = 300):  # 5 minutos por defecto
    """
    Decorador para cachear respuestas de funciones asíncronas.
    
    Args:
        ttl: Tiempo de vida del caché en segundos
    """
    def decorator(func: Callable) -> Callable:
        @cached(
            ttl=ttl,
            serializer=PickleSerializer(),
            key_builder=lambda *args, **kwargs: f"{func.__name__}:{str(args)}:{str(kwargs)}"
        )
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error en función cacheada {func.__name__}: {str(e)}")
                raise

        return wrapper
    return decorator 