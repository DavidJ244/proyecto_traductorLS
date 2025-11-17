"""
Servicio de procesamiento de video
Orquesta la ejecución de los tres modelos de IA en secuencia
"""
import time
import uuid
import os
import logging
from typing import Dict
from pathlib import Path
from config import settings
from ai_services import (
    get_path_detection_service,
    get_gloss_generator_service,
    get_text_translation_service
)

logger = logging.getLogger(__name__)

# Almacenar estado de jobs en memoria (en producción, usar Redis/DB)
processing_jobs: Dict[str, Dict] = {}


class VideoProcessorService:
    """
    Servicio que orquesta todo el pipeline de procesamiento:
    1. Path Detection (Detección de cuerpo)
    2. Gloss Generator (Generación de glosa)
    3. Text Translation (Traducción a español)
    """
    
    def __init__(self):
        self.path_detection_service = None
        self.gloss_generator_service = None
        self.text_translation_service = None
    
    async def process_video_async(self, video_path: str, job_id: str) -> Dict:
        """
        Procesa un video de forma asíncrona a través del pipeline completo
        
        Flujo:
        1. Detectar pose del cuerpo en el video (Path Detection)
        2. Generar glosa basada en los keypoints (Gloss Generator)
        3. Traducir glosa a texto natural en español (Text Translation)
        
        Args:
            video_path: Ruta al archivo de video
            job_id: ID único del job de procesamiento
            
        Returns:
            Dict con resultado completo o error
        """
        
        try:
            overall_start = time.time()
            
            # Actualizar estado del job
            processing_jobs[job_id]["status"] = "processing"
            processing_jobs[job_id]["current_step"] = "Detecting pose (Path Detection)..."
            processing_jobs[job_id]["progress"] = 10
            
            logger.info(f"[Job {job_id}] Iniciando procesamiento de video: {video_path}")
            
            # ============================================================
            # PASO 1: PATH DETECTION - Detectar pose del cuerpo
            # ============================================================
            logger.info(f"[Job {job_id}] PASO 1: Ejecutando PATH DETECTION")
            processing_jobs[job_id]["current_step"] = "Detecting pose (Path Detection)..."
            processing_jobs[job_id]["progress"] = 15
            
            path_detection_service = await get_path_detection_service()
            path_detection_result = await path_detection_service.detect_pose_from_video(video_path)
            
            if not path_detection_result.get("success"):
                raise Exception(f"Path Detection falló: {path_detection_result.get('error')}")
            
            keypoints = path_detection_result.get("keypoints", [])
            logger.info(f"[Job {job_id}] Path Detection completado - {len(keypoints)} frames procesados")
            
            processing_jobs[job_id]["progress"] = 40
            processing_jobs[job_id]["path_detection"] = path_detection_result
            
            # ============================================================
            # PASO 2: GLOSS GENERATOR - Generar glosa
            # ============================================================
            logger.info(f"[Job {job_id}] PASO 2: Ejecutando GLOSS GENERATOR")
            processing_jobs[job_id]["current_step"] = "Generating gloss (Recurrent Model)..."
            processing_jobs[job_id]["progress"] = 50
            
            gloss_generator_service = await get_gloss_generator_service()
            gloss_result = await gloss_generator_service.generate_gloss(keypoints)
            
            if not gloss_result.get("success"):
                raise Exception(f"Gloss Generator falló: {gloss_result.get('error')}")
            
            gloss_text = gloss_result.get("gloss", "")
            logger.info(f"[Job {job_id}] Gloss Generator completado - Glosa: {gloss_text}")
            
            processing_jobs[job_id]["progress"] = 70
            processing_jobs[job_id]["gloss_generation"] = gloss_result
            
            # ============================================================
            # PASO 3: TEXT TRANSLATION - Traducir glosa a español
            # ============================================================
            logger.info(f"[Job {job_id}] PASO 3: Ejecutando TEXT TRANSLATION")
            processing_jobs[job_id]["current_step"] = "Translating to Spanish (Text Generator)..."
            processing_jobs[job_id]["progress"] = 80
            
            text_translation_service = await get_text_translation_service()
            translation_result = await text_translation_service.translate_gloss_to_text(gloss_text)
            
            if not translation_result.get("success"):
                raise Exception(f"Text Translation falló: {translation_result.get('error')}")
            
            translation_text = translation_result.get("translation", "")
            logger.info(f"[Job {job_id}] Text Translation completado - Traducción: {translation_text}")
            
            processing_jobs[job_id]["progress"] = 95
            processing_jobs[job_id]["text_translation"] = translation_result
            
            # ============================================================
            # COMPLETADO - Compilar resultado final
            # ============================================================
            total_time_ms = (time.time() - overall_start) * 1000
            
            final_result = {
                "success": True,
                "job_id": job_id,
                "status": "completed",
                "path_detection": path_detection_result,
                "gloss_generation": gloss_result,
                "text_translation": translation_result,
                "total_processing_time_ms": total_time_ms,
                "final_gloss": gloss_text,
                "final_translation": translation_text
            }
            
            processing_jobs[job_id]["status"] = "completed"
            processing_jobs[job_id]["progress"] = 100
            processing_jobs[job_id]["result"] = final_result
            
            logger.info(f"[Job {job_id}] Procesamiento completado exitosamente en {total_time_ms:.2f}ms")
            
            return final_result
        
        except Exception as e:
            logger.error(f"[Job {job_id}] Error en procesamiento: {str(e)}")
            
            error_result = {
                "success": False,
                "job_id": job_id,
                "status": "error",
                "error": str(e),
                "total_processing_time_ms": (time.time() - overall_start) * 1000
            }
            
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["error"] = str(e)
            
            return error_result
    
    async def save_result(self, job_id: str, result: Dict) -> str:
        """
        Guarda el resultado del procesamiento en un archivo JSON
        
        Args:
            job_id: ID del job
            result: Resultado del procesamiento
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            results_dir = Path(settings.RESULTS_DIR)
            results_dir.mkdir(parents=True, exist_ok=True)
            
            result_file = results_dir / f"{job_id}_result.json"
            
            import json
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Resultado guardado en: {result_file}")
            return str(result_file)
        
        except Exception as e:
            logger.error(f"Error guardando resultado: {str(e)}")
            return ""


def create_video_processor_service() -> VideoProcessorService:
    """Factory para crear instancia del servicio"""
    return VideoProcessorService()


def get_job_status(job_id: str) -> Dict:
    """Obtiene el estado actual de un job"""
    if job_id not in processing_jobs:
        return {
            "job_id": job_id,
            "status": "not_found",
            "progress": 0,
            "current_step": "Unknown"
        }
    
    job = processing_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "current_step": job.get("current_step", ""),
        "result": job.get("result", None) if job.get("status") == "completed" else None,
        "error": job.get("error", None) if job.get("status") == "error" else None
    }


def create_new_job(video_filename: str) -> str:
    """
    Crea un nuevo job de procesamiento
    
    Args:
        video_filename: Nombre del archivo de video
        
    Returns:
        ID único del job
    """
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {
        "status": "pending",
        "video_filename": video_filename,
        "progress": 0,
        "current_step": "Waiting to start...",
        "created_at": time.time()
    }
    return job_id
