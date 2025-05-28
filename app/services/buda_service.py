from typing import Dict, Optional
import httpx
from datetime import datetime
import logging
from app.exceptions.currency_exceptions import BudaAPIError, CurrencyNotFoundError
from app.core.circuit_breaker import circuit_breaker
from app.core.cache import cache_response

logger = logging.getLogger(__name__)

class BudaService:
    BASE_URL = "https://www.buda.com/api/v2"
    TIMEOUT = 10.0  # segundos
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=self.TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    @circuit_breaker
    @cache_response(ttl=60)  # Cachear por 1 minuto
    async def get_market_ticker(self, market_id: str) -> Dict:
        """
        Obtiene el último precio de un mercado específico.
        """
        try:
            response = await self.client.get(
                f"/markets/{market_id}/ticker",
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise CurrencyNotFoundError(
                    f"Mercado {market_id} no encontrado",
                    {"market_id": market_id}
                )
            raise BudaAPIError(
                f"Error al obtener ticker del mercado {market_id}",
                {"market_id": market_id, "status_code": e.response.status_code}
            )
        except httpx.RequestError as e:
            raise BudaAPIError(
                f"Error de conexión con Buda API: {str(e)}",
                {"market_id": market_id}
            )
        except httpx.TimeoutException as e:
            raise BudaAPIError(
                f"Timeout al conectar con Buda API: {str(e)}",
                {"market_id": market_id}
            )
    
    @circuit_breaker
    @cache_response(ttl=300)  # Cachear por 5 minutos
    async def get_available_markets(self) -> Dict:
        """
        Obtiene todos los mercados disponibles.
        """
        try:
            response = await self.client.get(
                "/markets",
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BudaAPIError(
                "Error al obtener mercados disponibles",
                {"status_code": e.response.status_code}
            )
        except httpx.RequestError as e:
            raise BudaAPIError(
                f"Error de conexión con Buda API: {str(e)}"
            )
        except httpx.TimeoutException as e:
            raise BudaAPIError(
                f"Timeout al conectar con Buda API: {str(e)}"
            )
    
    async def close(self):
        """
        Cierra el cliente HTTP.
        """
        await self.client.aclose() 