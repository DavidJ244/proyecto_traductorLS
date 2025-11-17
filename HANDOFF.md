# INSTRUCCIONES PARA INTEGRAR MODELOS REALES

**Para:** Desarrollador de IA  
**De:** Desarrollador Backend  
**Fecha:** 2025-11-17  
**Estado:** Backend LISTO y PROBADO ✅

---

## Resumen

El backend está **100% funcional** con modelos MOCK (simulados). Tu tarea es:

1. Reemplazar los servicios MOCK con tus modelos reales de IA
2. Probar el pipeline completo
3. Desplegar en AWS

---

## Estructura del Proyecto

```
backend/
├── app.py                    ← Servidor FastAPI (NO TOCAR)
├── config.py                 ← Configuración (NO TOCAR)
├── .env.local                ← Variables de entorno (AJUSTAR)
├── requirements.txt          ← Dependencias Python
├── models_schemas.py         ← Modelos Pydantic (NO TOCAR)
├── ai_services.py            ← ★★★ TUS MODELOS VAN AQUÍ ★★★
├── video_processor.py        ← Orquestador (NO TOCAR)
├── video_routes.py           ← Endpoints (NO TOCAR)
├── health_routes.py          ← Health checks (NO TOCAR)
├── API_DOCUMENTATION.md      ← Documentación de endpoints
└── uploads/
    ├── videos/
    └── results/
```

---

## ¿Dónde van tus modelos?

### Archivo: `backend/ai_services.py`

Este archivo tiene **3 servicios** que están en modo MOCK:

#### 1. Path Detection Service (~línea 50-120)

**Tu modelo:** Detecta pose/movimientos del cuerpo en el video

**Input esperado:**
```python
video_path: str  # Ruta al archivo .mp4
```

**Output esperado:**
```python
{
    "success": True,
    "keypoints": [[x1, y1, z1], [x2, y2, z2], ...],  # Lista de keypoints por frame
    "confidence": 0.95,  # 0.0 - 1.0
    "frames_processed": 300,
    "detection_time_ms": 2500
}
```

**Código actual (MOCK):**
```python
class PathDetectionServiceImpl(PathDetectionService):
    async def detect_pose_from_video(self, video_path: str) -> Dict:
        # ← REEMPLAZA ESTO CON TU MODELO
        await asyncio.sleep(2.5)  # Simula procesamiento
        return {...}  # Datos simulados
```

**Cómo integrarlo:**
1. Carga tu modelo entrenado (MediaPipe, OpenPose, etc.)
2. Procesa el video frame por frame
3. Extrae keypoints
4. Retorna el diccionario con el formato esperado

---

#### 2. Gloss Generator Service (~línea 125-200)

**Tu modelo:** Genera glosa (texto de señas) a partir de keypoints

**Input esperado:**
```python
keypoints: List[List[float]]  # Keypoints del Path Detection
```

**Output esperado:**
```python
{
    "success": True,
    "gloss": "CASA TECHO GATO ESTAR-AHÍ",  # Glosa generada
    "confidence": 0.92,  # 0.0 - 1.0
    "processing_time_ms": 1800
}
```

**Código actual (MOCK):**
```python
class GlossGeneratorServiceImpl(GlossGeneratorService):
    async def generate_gloss(self, keypoints: List[List[float]]) -> Dict:
        # ← REEMPLAZA ESTO CON TU MODELO RECURRENTE (LSTM/Transformer)
        await asyncio.sleep(1.8)
        return {...}
```

**Cómo integrarlo:**
1. Carga tu modelo recurrente (LSTM, Transformer, etc.)
2. Procesa la secuencia de keypoints
3. Genera la glosa
4. Retorna el diccionario con el formato esperado

---

#### 3. Text Translation Service (~línea 205-280)

**Tu modelo:** Traduce glosa a español natural

**Input esperado:**
```python
gloss: str  # Por ejemplo: "CASA TECHO GATO ESTAR-AHÍ"
```

**Output esperado:**
```python
{
    "success": True,
    "translation": "El gato está en el techo de la casa",
    "confidence": 0.88,  # 0.0 - 1.0
    "processing_time_ms": 950
}
```

**Código actual (MOCK):**
```python
class TextTranslationServiceImpl(TextTranslationService):
    async def translate_gloss_to_text(self, gloss: str) -> Dict:
        # ← REEMPLAZA ESTO CON TU MODELO GENERADOR (T5/MarianMT/LLM)
        await asyncio.sleep(0.95)
        return {...}
```

**Cómo integrarlo:**
1. Carga tu modelo generador de texto (T5, MarianMT, etc.)
2. Traduce la glosa a español
3. Retorna el diccionario con el formato esperado

---

## Flujo Completo (cómo funciona)

```
VIDEO SUBIDO
    ↓
1. Path Detection (tu modelo 1)
    └─ Detecta keypoints
    ↓
2. Gloss Generator (tu modelo 2)
    └─ Genera glosa
    ↓
3. Text Translation (tu modelo 3)
    └─ Traduce a español
    ↓
RESULTADO FINAL
```

---

## Setup Local

### Requisitos

- Python 3.11 o 3.12 (recomendado para compatibilidad con MediaPipe si lo usas)
- Git

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/proyecto-sena-traduccion.git
cd proyecto-sena-traduccion/backend

# 2. Crear entorno virtual
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env.local
# Edita .env.local con tu configuración

# 5. Ejecutar servidor
python app.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Testing

### Con Swagger UI (recomendado)

1. Abre `http://localhost:8000/docs`
2. Prueba el flujo completo:
   - POST /api/upload-video
   - POST /api/process-video/{job_id}
   - GET /api/status/{job_id}
   - GET /api/result/{job_id}

### Con cURL

```bash
# 1. Subir video
curl -X POST http://localhost:8000/api/upload-video -F "file=@test.mp4"
# Copiar job_id

# 2. Procesar
curl -X POST http://localhost:8000/api/process-video/JOB_ID

# 3. Consultar estado
curl http://localhost:8000/api/status/JOB_ID

# 4. Obtener resultado
curl http://localhost:8000/api/result/JOB_ID
```

---

## Checklist de Integración

- [ ] Cloné el repositorio
- [ ] Instalé las dependencias
- [ ] El backend corre sin errores (con MOCKs)
- [ ] Probé el flujo completo en Swagger
- [ ] Entiendo dónde van mis modelos (`ai_services.py`)
- [ ] Cargué mi modelo de Path Detection
- [ ] Cargué mi modelo de Gloss Generator
- [ ] Cargué mi modelo de Text Translation
- [ ] Probé el flujo completo con modelos reales
- [ ] Todo funciona end-to-end

---

## Deployment a AWS

Una vez que tus modelos funcionen localmente:

1. Crear instancia EC2 en AWS Academy
2. Instalar Python 3.11
3. Clonar repositorio
4. Configurar `.env.production`
5. Instalar dependencias
6. Configurar Nginx como reverse proxy
7. Usar systemd para mantener el servidor corriendo
8. (Opcional) Configurar S3 para almacenamiento de videos

---

## Dudas o Problemas

Si tienes dudas:

1. Lee `API_DOCUMENTATION.md` (documentación completa de endpoints)
2. Lee `README.md` (guía general del proyecto)
3. Revisa los logs del backend (se muestran en la terminal)
4. Contacta al desarrollador backend

---

## Estado Actual

✅ Backend funcional  
✅ API REST documentada  
✅ Pipeline MOCK probado  
✅ Swagger UI funcional  
✅ Health checks funcionando  
⏳ Modelos reales pendientes (TU TAREA)  

---

**¡Éxito con la integración!** 🚀
