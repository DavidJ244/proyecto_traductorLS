"""
Rutas (Endpoints) de la API para video
"""
import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from config import settings
from models_schemas import ProcessingResponse, StatusQueryResponse
from video_processor import (
    create_video_processor_service,
    get_job_status,
    create_new_job
)
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["video"])


@router.post("/upload-video", response_model=dict)
async def upload_video(file: UploadFile = File(...)):
    """
    Endpoint para cargar un video
    
    Request: multipart/form-data con archivo de video
    Response: job_id para hacer polling del estado
    
    Ejemplo:
        POST /api/upload-video
        Content-Type: multipart/form-data
        Body: video file
    """
    try:
        # Validar que sea un archivo de video
        if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            raise HTTPException(status_code=400, detail="Solo se aceptan archivos de video")
        
        # Crear job nuevo
        job_id = create_new_job(file.filename)
        logger.info(f"[Job {job_id}] Video uploaded: {file.filename}")
        
        # Guardar archivo
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{job_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"[Job {job_id}] Archivo guardado - Tamaño: {file_size} bytes")
        
        # Validar tamaño
        max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            os.remove(file_path)
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo: {settings.MAX_VIDEO_SIZE_MB}MB"
            )
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Video cargado exitosamente",
            "filename": file.filename,
            "file_size": file_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al cargar video: {str(e)}")


@router.post("/process-video/{job_id}")
async def process_video(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para procesar un video
    
    Pipeline de procesamiento:
    1. Path Detection - Detecta la pose del cuerpo
    2. Gloss Generator - Genera glosa (representación de señas)
    3. Text Translation - Traduce glosa a español
    
    Request: POST /api/process-video/{job_id}
    Response: Estado del procesamiento + job_id
    
    Flujo esperado:
    - El cliente recibe una respuesta inmediata con status "processing"
    - El cliente hace polling a /api/status/{job_id} para obtener resultado
    """
    try:
        # Verificar que el job existe
        job_status = get_job_status(job_id)
        if job_status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado")
        
        # Encontrar el archivo de video
        upload_dir = Path(settings.UPLOAD_DIR)
        video_files = list(upload_dir.glob(f"{job_id}_*"))
        
        if not video_files:
            raise HTTPException(status_code=404, detail="Archivo de video no encontrado")
        
        video_path = str(video_files[0])
        logger.info(f"[Job {job_id}] Iniciando procesamiento de: {video_path}")
        
        # Ejecutar procesamiento en background
        processor = create_video_processor_service()
        background_tasks.add_task(
            processor.process_video_async,
            video_path,
            job_id
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "processing",
            "message": "Procesamiento iniciado. Usa GET /api/status/{job_id} para consultar el estado.",
            "poll_url": f"/api/status/{job_id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en process_video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/status/{job_id}", response_model=dict)
async def get_status(job_id: str):
    """
    Endpoint para consultar el estado del procesamiento
    
    Request: GET /api/status/{job_id}
    Response: Estado actual, progreso y resultado si está completado
    
    Estados posibles:
    - pending: Esperando para iniciar
    - processing: En procesamiento
    - completed: Completado exitosamente
    - error: Error durante procesamiento
    - not_found: Job no existe
    """
    try:
        status = get_job_status(job_id)
        
        return {
            "success": True,
            "job_id": job_id,
            "status": status["status"],
            "progress": status["progress"],
            "current_step": status["current_step"],
            "result": status.get("result"),
            "error": status.get("error")
        }
    
    except Exception as e:
        logger.error(f"Error en get_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    """
    Endpoint para obtener el resultado final del procesamiento
    
    Request: GET /api/result/{job_id}
    Response: Glosa y traducción final
    
    Respuesta esperada:
    {
        "success": true,
        "gloss": "CASA TECHO GATO ESTAR-AHÍ",
        "translation": "El gato está en el techo de la casa",
        "confidence_gloss": 0.92,
        "confidence_translation": 0.88,
        "processing_time_ms": 5250
    }
    """
    try:
        status = get_job_status(job_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado")
        
        if status["status"] != "completed":
            raise HTTPException(
                status_code=202,
                detail=f"Job aún no completado. Estado actual: {status['status']}"
            )
        
        result = status.get("result", {})
        
        return {
            "success": True,
            "job_id": job_id,
            "gloss": result.get("final_gloss", ""),
            "translation": result.get("final_translation", ""),
            "confidence_gloss": result.get("gloss_generation", {}).get("confidence", 0),
            "confidence_translation": result.get("text_translation", {}).get("confidence", 0),
            "processing_time_ms": result.get("total_processing_time_ms", 0),
            "detailed_results": {
                "path_detection": result.get("path_detection"),
                "gloss_generation": result.get("gloss_generation"),
                "text_translation": result.get("text_translation")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en get_result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
