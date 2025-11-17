"""
Modelos de datos Pydantic para la aplicación
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class VideoMetadata(BaseModel):
    """Metadatos del video"""
    video_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_size: int
    duration: float
    width: int
    height: int
    fps: int
    upload_time: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "video_1.mp4",
                "file_size": 5242880,
                "duration": 10.5,
                "width": 1280,
                "height": 720,
                "fps": 30
            }
        }


class PathDetectionResult(BaseModel):
    """Resultado de detección de pose/path"""
    job_id: str
    keypoints: List[List[float]] = Field(description="Puntos clave detectados")
    confidence: float = Field(ge=0, le=1, description="Confianza de la detección")
    frames_processed: int
    detection_time_ms: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "keypoints": [[100, 200], [150, 250], [200, 180]],
                "confidence": 0.95,
                "frames_processed": 300,
                "detection_time_ms": 2500
            }
        }


class GlossGeneratorResult(BaseModel):
    """Resultado de generación de glosa"""
    job_id: str
    gloss: str = Field(description="Glosa identificada")
    confidence: float = Field(ge=0, le=1)
    processing_time_ms: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "gloss": "CASA TECHO GATO ESTAR-AHÍ",
                "confidence": 0.92,
                "processing_time_ms": 1800
            }
        }


class TextTranslationResult(BaseModel):
    """Resultado de traducción a texto natural"""
    job_id: str
    gloss: str
    translation: str = Field(description="Traducción al español")
    confidence: float = Field(ge=0, le=1)
    processing_time_ms: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "gloss": "CASA TECHO GATO ESTAR-AHÍ",
                "translation": "El gato está en el techo de la casa",
                "confidence": 0.88,
                "processing_time_ms": 950
            }
        }


class ProcessingResponse(BaseModel):
    """Respuesta completa del procesamiento"""
    job_id: str
    status: str = Field(description="Estado: pending, processing, completed, error")
    video_metadata: Optional[VideoMetadata] = None
    path_detection: Optional[PathDetectionResult] = None
    gloss_generation: Optional[GlossGeneratorResult] = None
    text_translation: Optional[TextTranslationResult] = None
    error: Optional[str] = None
    total_processing_time_ms: float = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "gloss_generation": {
                    "gloss": "CASA TECHO GATO ESTAR-AHÍ",
                    "confidence": 0.92
                },
                "text_translation": {
                    "translation": "El gato está en el techo de la casa",
                    "confidence": 0.88
                },
                "total_processing_time_ms": 5250
            }
        }


class UploadVideoRequest(BaseModel):
    """Request para upload de video"""
    filename: str = Field(description="Nombre del archivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "seña_gato.mp4"
            }
        }


class StatusQueryResponse(BaseModel):
    """Respuesta de consulta de estado"""
    job_id: str
    status: str = Field(description="pending, processing, completed, error")
    progress: int = Field(ge=0, le=100, description="Porcentaje de progreso")
    current_step: str = Field(description="Paso actual del procesamiento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "progress": 65,
                "current_step": "Generating gloss..."
            }
        }


class HealthCheckResponse(BaseModel):
    """Respuesta de health check"""
    status: str = Field(description="healthy, degraded, unhealthy")
    version: str
    environment: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "timestamp": "2025-11-14T12:00:00"
            }
        }
