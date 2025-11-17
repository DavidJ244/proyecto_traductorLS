"""
Rutas de Health Check
"""
import logging
from fastapi import APIRouter
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
@router.get("/")
async def health_check():
    """
    Health check endpoint
    
    Retorna el estado de la aplicación
    Útil para verificar que el servidor está corriendo
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development",
        "timestamp": datetime.now().isoformat(),
        "message": "Sign Language Translation API is running"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Verifica que la aplicación está lista para recibir requests
    """
    return {
        "ready": True,
        "timestamp": datetime.now().isoformat()
    }
