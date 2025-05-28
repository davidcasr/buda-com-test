from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime


class ConversionResponse(BaseModel):
    final_amount: Decimal = Field(..., description="Monto final después de la conversión")
    intermediate_currency: str = Field(..., description="Criptomoneda usada como intermediaria")
    from_currency: str = Field(..., description="Moneda de origen")
    to_currency: str = Field(..., description="Moneda de destino")
    original_amount: Decimal = Field(..., description="Monto original a convertir")
    conversion_rate: Optional[Decimal] = Field(None, description="Tasa de conversión efectiva")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la conversión")
    
    class Config:
        schema_extra = {
            "example": {
                "final_amount": "1234.56",
                "intermediate_currency": "BTC",
                "from_currency": "CLP",
                "to_currency": "PEN",
                "original_amount": "1000000",
                "conversion_rate": "0.001234",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado general del servicio")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Versión de la aplicación")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        }


class ReadinessResponse(BaseModel):
    status: str = Field(..., description="Estado de preparación del servicio")
    dependencies: Dict[str, str] = Field(..., description="Estado de las dependencias")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks_passed: int = Field(..., description="Número de checks que pasaron")
    checks_total: int = Field(..., description="Número total de checks")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "ready",
                "dependencies": {
                    "buda_api": "healthy",
                    "cache": "healthy"
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "checks_passed": 2,
                "checks_total": 2
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Error de validación en los parámetros de entrada",
                "details": {
                    "field": "amount",
                    "issue": "debe ser mayor que 0"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        } 