# API de Traducción de Lengua de Señas - Documentación

## Descripción General

API REST para traducir videos de lengua de señas a texto en español.

**Pipeline de procesamiento:**
1. **Path Detection**: Detecta la pose/movimientos del cuerpo en el video
2. **Gloss Generator**: Genera glosa (representación de señas en texto)
3. **Text Translation**: Traduce glosa a español natural

---

## Endpoints Principales

### 1. Health Check (Verificar que la API está viva)

```
GET /health
GET /health/ready
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-11-16T09:57:00",
  "message": "Sign Language Translation API is running"
}
```

---

### 2. Subir Video

```
POST /api/upload-video
Content-Type: multipart/form-data

Body: file (archivo .mp4)
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Video cargado exitosamente",
  "filename": "video.mp4",
  "file_size": 5242880
}
```

**Errores:**
- 400: Archivo no es video (.mp4, .mov, .avi, .mkv)
- 413: Archivo mayor a MAX_VIDEO_SIZE_MB (default 100)
- 500: Error interno

---

### 3. Iniciar Procesamiento

```
POST /api/process-video/{job_id}
```

**Parámetros:**
- `job_id`: ID retornado por /upload-video

**Respuesta (202):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Procesamiento iniciado. Usa GET /api/status/{job_id} para consultar el estado.",
  "poll_url": "/api/status/550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 4. Consultar Estado

```
GET /api/status/{job_id}
```

**Respuesta:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "current_step": "Translating to Spanish...",
  "result": null,
  "error": null
}
```

**Estados posibles:**
- `pending`: Esperando procesamiento
- `processing`: En proceso
- `completed`: Completado
- `error`: Error durante procesamiento

---

### 5. Obtener Resultado Final

```
GET /api/result/{job_id}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "gloss": "CASA TECHO GATO ESTAR-AHÍ",
  "translation": "El gato está en el techo de la casa",
  "confidence_gloss": 0.92,
  "confidence_translation": 0.88,
  "processing_time_ms": 5250,
  "detailed_results": {
    "path_detection": {
      "success": true,
      "keypoints": [...],
      "confidence": 0.95,
      "frames_processed": 300,
      "detection_time_ms": 2500
    },
    "gloss_generation": {
      "success": true,
      "gloss": "CASA TECHO GATO ESTAR-AHÍ",
      "confidence": 0.92,
      "processing_time_ms": 1800
    },
    "text_translation": {
      "success": true,
      "translation": "El gato está en el techo de la casa",
      "confidence": 0.88,
      "processing_time_ms": 950
    }
  }
}
```

---

## Flujo de Uso Completo

### Cliente (App móvil)

```
1. POST /api/upload-video
   ↓ (recibe job_id)
2. POST /api/process-video/{job_id}
   ↓ (recibe "processing")
3. LOOP: GET /api/status/{job_id}
   ├─ Si status == "completed": ir a paso 4
   ├─ Si status == "error": mostrar error
   └─ Si status == "processing": esperar y reintentar
4. GET /api/result/{job_id}
   ↓ (recibe gloss + translation)
5. Mostrar resultado al usuario
```

---

## Variables de Entorno (.env.local o .env.production)

```env
# Servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Rutas de almacenamiento
UPLOAD_DIR=./uploads/videos
RESULTS_DIR=./uploads/results

# Configuración de video
MAX_VIDEO_SIZE_MB=100
MAX_VIDEO_DURATION_SECONDS=15
VIDEO_RESOLUTION_WIDTH=1280
VIDEO_RESOLUTION_HEIGHT=720
VIDEO_FPS=30

# Modelos IA
USE_MOCK_MODELS=True  # Cambiar a False cuando tengas modelos reales

# APIs de tus modelos reales (cuando integres)
PATH_DETECTION_API_URL=http://localhost:5000/detect
GLOSS_GENERATOR_API_URL=http://localhost:5001/generate
TEXT_TRANSLATION_API_URL=http://localhost:5002/translate

# CORS
CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

---

## Integración de Modelos Reales

### Para tu compañero: Dónde implementar

**Archivo:** `backend/ai_services.py`

#### Path Detection Service (Líneas ~50-120)

```python
class PathDetectionServiceImpl(PathDetectionService):
    async def detect_pose_from_video(self, video_path: str) -> Dict:
        """
        Reemplazar el mock por:
        1. Cargar tu modelo Path Detection
        2. Procesar video frame por frame
        3. Retornar keypoints, confianza, tiempos
        """
        # TU CÓDIGO AQUÍ
```

**Input esperado:**
- `video_path`: ruta al archivo .mp4

**Output esperado:**
```python
{
    "success": True,
    "keypoints": [[x1, y1, z1], [x2, y2, z2], ...],  # Coordenadas de cada frame
    "confidence": 0.95,  # 0-1
    "frames_processed": 300,
    "detection_time_ms": 2500
}
```

#### Gloss Generator Service (Líneas ~125-200)

```python
class GlossGeneratorServiceImpl(GlossGeneratorService):
    async def generate_gloss(self, keypoints: List[List[float]]) -> Dict:
        """
        Reemplazar el mock por:
        1. Cargar tu modelo recurrente (LSTM/Transformer)
        2. Procesar keypoints
        3. Retornar glosa, confianza, tiempos
        """
        # TU CÓDIGO AQUÍ
```

**Input esperado:**
- `keypoints`: Lista de frames de keypoints del Path Detection

**Output esperado:**
```python
{
    "success": True,
    "gloss": "CASA TECHO GATO ESTAR-AHÍ",
    "confidence": 0.92,
    "processing_time_ms": 1800
}
```

#### Text Translation Service (Líneas ~205-280)

```python
class TextTranslationServiceImpl(TextTranslationService):
    async def translate_gloss_to_text(self, gloss: str) -> Dict:
        """
        Reemplazar el mock por:
        1. Cargar tu modelo T5/MarianMT/LLM
        2. Traducir glosa a español
        3. Retornar traducción, confianza, tiempos
        """
        # TU CÓDIGO AQUÍ
```

**Input esperado:**
- `gloss`: "CASA TECHO GATO ESTAR-AHÍ"

**Output esperado:**
```python
{
    "success": True,
    "translation": "El gato está en el techo de la casa",
    "confidence": 0.88,
    "processing_time_ms": 950
}
```

---

## Testing

### Con cURL

```bash
# 1. Subir video
curl -X POST http://localhost:8000/api/upload-video -F "file=@test.mp4"
# Obtener job_id de la respuesta

# 2. Procesar
curl -X POST http://localhost:8000/api/process-video/JOB_ID

# 3. Consultar estado
curl http://localhost:8000/api/status/JOB_ID

# 4. Obtener resultado
curl http://localhost:8000/api/result/JOB_ID
```

### Con Swagger UI

Abre en navegador: `http://localhost:8000/docs`

Prueba todos los endpoints desde la interfaz interactiva.

---

## Troubleshooting

- **"No module named 'mediapipe'"**: Normal en Python 3.13. No se instala porque no hay wheel oficial.
- **"Form data requires python-multipart"**: Instalar con `pip install python-multipart`
- **"Address already in use port 8000"**: Otro proceso usa ese puerto. Cambiar PORT en .env o matar el proceso.
- **"getaddrinfo failed al instalar paquetes"**: Problema de conexión a internet/PyPI.

