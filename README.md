# API de Conversión de Monedas

API REST que permite convertir monedas fiat (CLP, COP, PEN) usando criptomonedas como intermediarias (BTC, ETH, LTC, BCH) a través de la API de Buda.com.

## 🛠️ Instalación y Ejecución

1. Clona el repositorio:

```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Construye y ejecuta el contenedor:

```bash
docker-compose up --build
```

La aplicación estará disponible en http://localhost:8000

## 🧪 Ejecutar Tests

Para ejecutar los tests usando Docker:

```bash
docker-compose run --rm api pytest
```

Para ejecutar tests con cobertura:

```bash
docker-compose run --rm api pytest --cov=app
```

## 📚 Documentación de la API

Una vez que la aplicación esté en ejecución, puedes acceder a la documentación automática en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### GET /health

Verifica el estado de la API.

#### GET /convert

Convierte un monto de una moneda fiat a otra.

Parámetros:

- `from_currency`: Moneda de origen (CLP, COP o PEN)
- `to_currency`: Moneda de destino (CLP, COP o PEN)
- `amount`: Monto a convertir

Ejemplo de respuesta:

```json
{
  "final_amount": 1234.56,
  "intermediate_currency": "BTC",
  "from_currency": "CLP",
  "to_currency": "PEN",
  "original_amount": 1000000
}
```

Made with ❤️ by @davidcasr
