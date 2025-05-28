from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Literal
from app.models.currency import FiatCurrency


class ConversionRequest(BaseModel):
    from_currency: Literal["CLP", "COP", "PEN"] = Field(
        ..., 
        description="Moneda de origen (CLP, COP o PEN)"
    )
    to_currency: Literal["CLP", "COP", "PEN"] = Field(
        ..., 
        description="Moneda de destino (CLP, COP o PEN)"
    )
    amount: Decimal = Field(
        ..., 
        gt=0, 
        le=Decimal("1000000000"),
        description="Monto a convertir (debe ser mayor que 0 y menor o igual a 1,000,000,000)"
    )
    
    @validator('amount')
    def validate_amount_precision(cls, v):
        """Validar que el monto no tenga más de 8 decimales"""
        if v.as_tuple().exponent < -8:
            raise ValueError('El monto no puede tener más de 8 decimales')
        return v
    
    @validator('to_currency')
    def validate_different_currencies(cls, v, values):
        """Validar que las monedas de origen y destino sean diferentes"""
        if 'from_currency' in values and v == values['from_currency']:
            raise ValueError('Las monedas de origen y destino deben ser diferentes')
        return v
    
    @validator('from_currency', 'to_currency')
    def validate_supported_currency(cls, v):
        """Validar que la moneda esté soportada"""
        try:
            FiatCurrency(v)
        except ValueError:
            raise ValueError(f'Moneda {v} no soportada. Monedas válidas: CLP, COP, PEN')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "from_currency": "CLP",
                "to_currency": "PEN",
                "amount": "1000000"
            }
        } 