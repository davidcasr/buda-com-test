# API de Conversión de Monedas

API REST que permite convertir monedas fiat (CLP, COP, PEN) usando criptomonedas como intermediarias (BTC, ETH, LTC, BCH) a través de la API de Buda.com.

## 🚀 Características

- Conversión de monedas fiat usando criptomonedas como intermediarias
- Uso de precios en tiempo real de Buda.com
- API REST con FastAPI
- Tests automatizados
- Contenedorización con Docker

## 📋 Requisitos

- Python 3.11+
- Docker y Docker Compose (opcional)

## 🛠️ Instalación

### Usando Docker (recomendado)

1. Clona el repositorio:

```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Construye y ejecuta el contenedor:

```bash
docker-compose up --build
```

### Instalación local

1. Crea un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
uvicorn main:app --reload
```

## 🧪 Ejecutar tests

```bash
pytest
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

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
