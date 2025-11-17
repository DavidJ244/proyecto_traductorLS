"""
Punto de entrada principal de la aplicación FastAPI
Orquesta todos los componentes
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import settings
from video_routes import router as video_router
from health_routes import router as health_router

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sign Language Translation API",
    description="API para traducir lengua de señas a texto en español",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(health_router)
app.include_router(video_router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Welcome to Sign Language Translation API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health": "/health",
        "endpoints": {
            "upload_video": "POST /api/upload-video",
            "process_video": "POST /api/process-video/{job_id}",
            "get_status": "GET /api/status/{job_id}",
            "get_result": "GET /api/result/{job_id}"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Iniciando servidor en {settings.HOST}:{settings.PORT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Usando modelos MOCK: {settings.USE_MOCK_MODELS}")
    
    uvicorn.run(
        "app:app",  # ← Cambiar de app a "app:app" (STRING)
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

