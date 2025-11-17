# GUÍA RÁPIDA: IMPLEMENTAR MODELOS EN 5 PASOS

**Tiempo:** 30 minutos para entender todo

---

## PASO 1: Clonar y Setup (5 min)

```bash
# Clonar
git clone https://github.com/DavidJ244/proyecto_traductorLS.git
cd proyecto_traductorLS/backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt
```

✅ Verifica que corre:
```bash
python app.py
```

Abre: `http://localhost:8000/docs` (Swagger UI)

---

## PASO 2: Entender dónde va tu código (5 min)

Abre: `backend/ai_services.py`

Encontrarás esto:

```python
# 3 SERVICIOS - AQUÍ VAS A REEMPLAZAR EL CÓDIGO

1️⃣  PathDetectionServiceImpl     (línea ~50)   ← Detectar pose
2️⃣  GlossGeneratorServiceImpl     (línea ~125)  ← Generar glosa
3️⃣  TextTranslationServiceImpl    (línea ~205)  ← Traducir texto
```

Cada uno tiene un método `async` que debes completar.

---

## PASO 3: Primer servicio - Path Detection (10 min)

**¿QUÉ HACE?** Lee un video y detecta pose del cuerpo

**ABRE:** `backend/ai_services.py` línea ~50

**BUSCA ESTO:**
```python
class PathDetectionServiceImpl(PathDetectionService):
    async def detect_pose_from_video(self, video_path: str) -> Dict:
        # REEMPLAZA ESTO ↓
        await asyncio.sleep(2.5)
        return {...datos simulados...}
```

**REEMPLAZA CON TU CÓDIGO:**
```python
class PathDetectionServiceImpl(PathDetectionService):
    def __init__(self):
        # Cargar tu modelo en __init__
        import mediapipe as mp
        self.pose = mp.solutions.pose.Pose()
    
    async def detect_pose_from_video(self, video_path: str) -> Dict:
        import cv2
        import time
        
        start = time.time()
        cap = cv2.VideoCapture(video_path)
        keypoints = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            
            if results.pose_landmarks:
                kpts = [[l.x, l.y, l.z] for l in results.pose_landmarks.landmark]
                keypoints.append(kpts)
        
        cap.release()
        
        return {
            "success": True,
            "keypoints": keypoints,
            "confidence": 0.95,
            "frames_processed": len(keypoints),
            "detection_time_ms": int((time.time() - start) * 1000)
        }
```

✅ **Verifica:**
```bash
python app.py
# Abre http://localhost:8000/docs
# Sube un video y prueba
```

---

## PASO 4: Segundo servicio - Gloss Generator (10 min)

**¿QUÉ HACE?** Convierte keypoints a "CASA TECHO GATO..."

**ABRE:** `backend/ai_services.py` línea ~125

**REEMPLAZA:**
```python
class GlossGeneratorServiceImpl(GlossGeneratorService):
    def __init__(self):
        # Carga tu modelo LSTM/Transformer
        import tensorflow as tf
        self.model = tf.keras.models.load_model('path/to/your/model.h5')
    
    async def generate_gloss(self, keypoints: List[List[float]]) -> Dict:
        import numpy as np
        import time
        
        start = time.time()
        
        # Pasar keypoints por el modelo
        kpts_array = np.array(keypoints)
        predictions = self.model.predict(kpts_array)
        
        # Convertir predicciones a palabras
        gloss_words = ["PALABRA1", "PALABRA2", "PALABRA3"]  # Tus palabras
        gloss = " ".join(gloss_words)
        
        return {
            "success": True,
            "gloss": gloss,
            "confidence": 0.92,
            "processing_time_ms": int((time.time() - start) * 1000)
        }
```

---

## PASO 5: Tercer servicio - Text Translation (10 min)

**¿QUÉ HACE?** Convierte "CASA TECHO" a "La casa"

**ABRE:** `backend/ai_services.py` línea ~205

**REEMPLAZA:**
```python
class TextTranslationServiceImpl(TextTranslationService):
    def __init__(self):
        # Cargar modelo de traducción
        from transformers import pipeline
        self.translator = pipeline("text2text-generation", model="t5-base")
    
    async def translate_gloss_to_text(self, gloss: str) -> Dict:
        import time
        
        start = time.time()
        
        # Traducir con tu modelo
        prompt = f"Translate sign language: {gloss}"
        result = self.translator(prompt, max_length=100)
        translation = result[0]['generated_text']
        
        return {
            "success": True,
            "translation": translation,
            "confidence": 0.88,
            "processing_time_ms": int((time.time() - start) * 1000)
        }
```

---

## PRUEBA FINAL (5 min)

```bash
# 1. Asegúrate que el backend corre
python app.py

# 2. En otra terminal, haz una prueba
curl -X POST http://localhost:8000/api/upload-video \
  -F "file=@video.mp4"

# 3. Copia el job_id de la respuesta

# 4. Procesa
curl -X POST http://localhost:8000/api/process-video/JOB_ID

# 5. Consulta estado
curl http://localhost:8000/api/status/JOB_ID

# 6. Obtén resultado
curl http://localhost:8000/api/result/JOB_ID
```

✅ **DEBE DEVOLVER:**
```json
{
  "gloss": "TU_GLOSA_AQUI",
  "translation": "Tu traducción aquí",
  "confidence_gloss": 0.92,
  "confidence_translation": 0.88
}
```

---

## CHECKLIST RÁPIDO

- [ ] Cloné el repo
- [ ] Setup funciona
- [ ] Backend corre sin errores
- [ ] Reemplacé Path Detection
- [ ] Reemplacé Gloss Generator
- [ ] Reemplacé Text Translation
- [ ] Probé flujo completo
- [ ] Funciona! ✅

---

## ERRORES TÍPICOS

**Error:** `ModuleNotFoundError: No module named 'mediapipe'`
- Usa Python 3.11: `python3.11 -m venv venv`

**Error:** `Model file not found`
- Usa rutas absolutas o relativas al backend/

**Error:** `CUDA not available`
- Instala TensorFlow-GPU o usa CPU

**Error:** `Connection refused`
- ¿Está `python app.py` corriendo?

---

## ¿MÁS AYUDA?

Lee estos archivos (están en el repo):
- `backend/HANDOFF.md` - Instrucciones detalladas
- `backend/API_DOCUMENTATION.md` - Endpoints
- `GUIA_COMPAÑERO_IA.md` - Guía técnica completa

---

**¡Éxito!** 🚀
