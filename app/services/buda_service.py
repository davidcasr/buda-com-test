from typing import Dict, Optional
import httpx
from datetime import datetime

class BudaService:
    BASE_URL = "https://www.buda.com/api/v2"
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)
    
    async def get_market_ticker(self, market_id: str) -> Optional[Dict]:
        """
        Obtiene el último precio de un mercado específico.
        """
        try:
            response = await self.client.get(f"/markets/{market_id}/ticker")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None
    
    async def get_available_markets(self) -> Dict:
        """
        Obtiene todos los mercados disponibles.
        """
        response = await self.client.get("/markets")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """
        Cierra el cliente HTTP.
        """
        await self.client.aclose() 