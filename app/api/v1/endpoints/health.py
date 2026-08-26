from datetime import datetime

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Verificar estado de la API")
def check_health():
    """
    Endpoint de verificacion del estado del sistema.
    Retorna el nombre del proyecto, version y estado actual.
    """
    return HealthResponse(
        status="online",
        app_name=settings.PROJECT_NAME,
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )
