from enum import Enum


class FiatCurrency(str, Enum):
    """Enumeración de monedas fiat soportadas"""
    CLP = "CLP"
    COP = "COP"
    PEN = "PEN"


class CryptoCurrency(str, Enum):
    """Enumeración de criptomonedas soportadas como intermediarias"""
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    BCH = "BCH" 