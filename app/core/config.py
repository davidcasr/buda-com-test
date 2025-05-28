from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Información de la aplicación
    app_name: str = "Currency Conversion API"
    app_version: str = "1.0.0"
    app_description: str = "API para convertir monedas fiat usando criptomonedas como intermediarias"
    
    # Configuración de Buda API
    buda_api_url: str = "https://www.buda.com/api/v2"
    request_timeout: float = 10.0
    max_connections: int = 10
    max_keepalive_connections: int = 5
    
    # Configuración de caché
    cache_ttl_ticker: int = 60  # 1 minuto para tickers
    cache_ttl_markets: int = 300  # 5 minutos para mercados
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configuración de circuit breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30
    circuit_breaker_expected_exception: tuple = (Exception,)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = Settings() 