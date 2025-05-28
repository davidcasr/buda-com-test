from typing import Dict, Optional, Tuple
import logging
from app.models.currency import FiatCurrency, CryptoCurrency
from app.services.buda_service import BudaService
from app.exceptions.currency_exceptions import (
    ConversionError,
    CurrencyNotFoundError,
    InvalidAmountError,
    SameCurrencyError
)

logger = logging.getLogger(__name__)

class ConversionService:
    def __init__(self, buda_service: BudaService):
        self.buda_service = buda_service
        self.crypto_currencies = [CryptoCurrency.BTC, CryptoCurrency.ETH, CryptoCurrency.LTC, CryptoCurrency.BCH]
    
    async def get_conversion_rate(self, market_id: str) -> float:
        """
        Obtiene el último precio de un mercado específico.
        """
        try:
            ticker = await self.buda_service.get_market_ticker(market_id)
            if not ticker or "ticker" not in ticker:
                raise CurrencyNotFoundError(
                    f"No se encontró información de ticker para el mercado {market_id}",
                    {"market_id": market_id}
                )
            return float(ticker["ticker"]["last_price"][0])
        except ValueError as e:
            raise ConversionError(
                f"Error al procesar el precio del mercado {market_id}",
                {"market_id": market_id, "error": str(e)}
            )
    
    async def find_best_conversion(
        self,
        from_currency: FiatCurrency,
        to_currency: FiatCurrency,
        amount: float
    ) -> Tuple[float, CryptoCurrency]:
        """
        Encuentra la mejor ruta de conversión usando una criptomoneda como intermediaria.
        """
        if from_currency == to_currency:
            raise SameCurrencyError(
                "No se puede convertir entre la misma moneda",
                {"from_currency": from_currency, "to_currency": to_currency}
            )

        if amount <= 0:
            raise InvalidAmountError(
                "El monto a convertir debe ser mayor que cero",
                {"amount": amount}
            )

        best_final_amount = None
        best_intermediate = None
        conversion_errors = []

        for crypto in self.crypto_currencies:
            try:
                # Intentar comprar crypto con la moneda de origen
                buy_market = f"{crypto.value.lower()}-{from_currency.value.lower()}"
                buy_rate = await self.get_conversion_rate(buy_market)

                # Intentar vender crypto por la moneda de destino
                sell_market = f"{crypto.value.lower()}-{to_currency.value.lower()}"
                sell_rate = await self.get_conversion_rate(sell_market)

                # Calcular el monto final
                crypto_amount = amount / buy_rate
                final_amount = crypto_amount * sell_rate

                if best_final_amount is None or final_amount > best_final_amount:
                    best_final_amount = final_amount
                    best_intermediate = crypto

            except CurrencyNotFoundError as e:
                conversion_errors.append(str(e))
                continue
            except Exception as e:
                logger.error(f"Error en conversión con {crypto}: {str(e)}")
                conversion_errors.append(str(e))
                continue

        if not best_final_amount or not best_intermediate:
            raise ConversionError(
                "No se encontró una ruta de conversión válida",
                {
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "amount": amount,
                    "errors": conversion_errors
                }
            )

        return best_final_amount, best_intermediate 