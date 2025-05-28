from fastapi import APIRouter, HTTPException, Depends
from app.models.responses import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService
from app.core.config import settings
from app.core.dependencies import get_health_service

router = APIRouter(
    prefix="/health", 
    tags=["Health"],
    include_in_schema=False
)

@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Endpoint básico de health check.
    Retorna el estado general de la aplicación.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )

@router.get("/live", response_model=HealthResponse)
async def liveness_check(health_service: HealthService = Depends(get_health_service)):
    """
    Liveness probe - verifica si la aplicación está viva.
    """
    is_alive = await health_service.check_liveness()
    status = "healthy" if is_alive else "unhealthy"
    
    if not is_alive:
        raise HTTPException(status_code=503, detail="Service not alive")
    
    return HealthResponse(
        status=status,
        version=settings.app_version
    )

@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(health_service: HealthService = Depends(get_health_service)):
    """
    Readiness probe - verifica si la aplicación está lista para recibir tráfico.
    """
    is_ready, dependencies, checks_passed, checks_total = await health_service.check_readiness()
    
    status = "ready" if is_ready else "not_ready"
    
    if not is_ready:
        raise HTTPException(
            status_code=503, 
            detail={
                "status": status,
                "dependencies": dependencies,
                "checks_passed": checks_passed,
                "checks_total": checks_total
            }
        )
    
    return ReadinessResponse(
        status=status,
        dependencies=dependencies,
        checks_passed=checks_passed,
        checks_total=checks_total
    )
