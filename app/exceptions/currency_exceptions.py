from typing import Any, Dict, Optional

class CurrencyException(Exception):
    """Excepción base para errores relacionados con monedas."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class CurrencyValidationError(CurrencyException):
    """Error de validación de moneda."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class CurrencyNotFoundError(CurrencyException):
    """Error cuando no se encuentra una moneda o par de mercado."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ConversionError(CurrencyException):
    """Error durante el proceso de conversión."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)

class BudaAPIError(CurrencyException):
    """Error en la comunicación con la API de Buda."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)

class InvalidAmountError(CurrencyException):
    """Error cuando el monto a convertir es inválido."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class SameCurrencyError(CurrencyException):
    """Error cuando se intenta convertir entre la misma moneda."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details) 