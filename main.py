from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="API de Ejemplo")

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="OK",
        timestamp=datetime.now()
    ) 