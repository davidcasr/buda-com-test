from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class FiatCurrency(str, Enum):
    CLP = "CLP"
    COP = "COP"
    PEN = "PEN"

class CryptoCurrency(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    BCH = "BCH"

class ConversionRequest(BaseModel):
    from_currency: FiatCurrency = Field(..., description="Moneda de origen (CLP, COP o PEN)")
    to_currency: FiatCurrency = Field(..., description="Moneda de destino (CLP, COP o PEN)")
    amount: float = Field(..., gt=0, description="Monto a convertir")

class ConversionResponse(BaseModel):
    final_amount: float = Field(..., description="Monto final en la moneda de destino")
    intermediate_currency: CryptoCurrency = Field(..., description="Criptomoneda usada como intermediaria")
    from_currency: FiatCurrency = Field(..., description="Moneda de origen")
    to_currency: FiatCurrency = Field(..., description="Moneda de destino")
    original_amount: float = Field(..., description="Monto original en la moneda de origen") 