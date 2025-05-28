from typing import Dict, Optional, Tuple
from app.models.currency import FiatCurrency, CryptoCurrency
from app.services.buda_service import BudaService

class ConversionService:
    def __init__(self, buda_service: BudaService):
        self.buda_service = buda_service
        self.crypto_currencies = [CryptoCurrency.BTC, CryptoCurrency.ETH, CryptoCurrency.LTC, CryptoCurrency.BCH]
    
    async def get_conversion_rate(self, market_id: str) -> Optional[float]:
        """
        Obtiene el último precio de un mercado específico.
        """
        ticker = await self.buda_service.get_market_ticker(market_id)
        if not ticker or "ticker" not in ticker:
            return None
        return float(ticker["ticker"]["last_price"][0])
    
    async def find_best_conversion(
        self,
        from_currency: FiatCurrency,
        to_currency: FiatCurrency,
        amount: float
    ) -> Tuple[Optional[float], Optional[CryptoCurrency]]:
        """
        Encuentra la mejor ruta de conversión usando una criptomoneda como intermediaria.
        """
        best_final_amount = None
        best_intermediate = None

        for crypto in self.crypto_currencies:
            # Intentar comprar crypto con la moneda de origen
            buy_market = f"{crypto.value.lower()}-{from_currency.value.lower()}"
            buy_rate = await self.get_conversion_rate(buy_market)
            if not buy_rate:
                continue

            # Intentar vender crypto por la moneda de destino
            sell_market = f"{crypto.value.lower()}-{to_currency.value.lower()}"
            sell_rate = await self.get_conversion_rate(sell_market)
            if not sell_rate:
                continue

            # Calcular el monto final
            crypto_amount = amount / buy_rate
            final_amount = crypto_amount * sell_rate

            if best_final_amount is None or final_amount > best_final_amount:
                best_final_amount = final_amount
                best_intermediate = crypto

        return best_final_amount, best_intermediate 