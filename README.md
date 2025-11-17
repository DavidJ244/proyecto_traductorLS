# Sign Language Translation - Backend & Mobile

Sistema de traducción de lengua de señas a texto en español usando inteligencia artificial.

**Pipeline:**
1. **Path Detection**: Detección de pose/movimientos del cuerpo
2. **Gloss Generator**: Generación de glosa (seña en texto)
3. **Text Translation**: Traducción a español natural

---

## Estructura del Proyecto

```
proyecto-seña-traduccion/
├── backend/
│   ├── app.py                    ← Servidor FastAPI principal
│   ├── config.py                 ← Configuración y variables de entorno
│   ├── .env.local                ← Variables locales (no commitear)
│   ├── requirements.txt           ← Dependencias Python
│   ├── models_schemas.py         ← Modelos Pydantic
│   ├── ai_services.py            ← LOS 3 SERVICIOS DE IA (TU CÓDIGO VA AQUÍ)
│   ├── video_processor.py        ← Orquestador del pipeline
│   ├── video_routes.py           ← Endpoints de video
│   ├── health_routes.py          ← Health checks
│   ├── API_DOCUMENTATION.md      ← Documentación de endpoints
│   └── uploads/
│       ├── videos/               ← Videos grabados
│       └── results/              ← Resultados JSON
│
└── mobile/
    ├── lib/
    │   └── main.dart             ← App Flutter (iOS/Android)
    └── pubspec.yaml              ← Dependencias Flutter
```

---

## Quick Start - Backend

### Requisitos

- Python 3.13 (Windows, macOS, Linux)
- Git
- Visual Studio Code (opcional pero recomendado)

### Instalación Local

```bash
# 1. Clonar/descargar proyecto
cd proyecto-seña-traduccion/backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar servidor
python app.py
```

Verás:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Verificación

- **API Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

---

## Quick Start - Mobile (Flutter)

### Requisitos

- Flutter SDK
- Android Studio / Xcode
- Emulador o dispositivo físico

### Instalación Local

```bash
cd mobile

# Instalar dependencias
flutter pub get

# Ejecutar en emulador/dispositivo
flutter run
```

**Importante**: Antes de ejecutar, edita `lib/main.dart` línea 11:

```dart
// Android Emulator:
const String API_BASE_URL = "http://10.0.2.2:8000/api";

// iOS Simulator:
// const String API_BASE_URL = "http://localhost:8000/api";

// Dispositivo físico (cambiar IP):
// const String API_BASE_URL = "http://192.168.1.100:8000/api";
```

---

## Testing del Pipeline Completo

### Con Postman/cURL

```bash
# 1. Subir video
curl -X POST http://localhost:8000/api/upload-video \
  -F "file=@video_test.mp4"
# Obtener job_id de la respuesta

# 2. Procesar
curl -X POST http://localhost:8000/api/process-video/JOB_ID

# 3. Consultar estado (repetir hasta que status == "completed")
curl http://localhost:8000/api/status/JOB_ID

# 4. Obtener resultado final
curl http://localhost:8000/api/result/JOB_ID
```

### Respuesta esperada

```json
{
  "success": true,
  "gloss": "CASA TECHO GATO ESTAR-AHÍ",
  "translation": "El gato está en el techo de la casa",
  "confidence_gloss": 0.92,
  "confidence_translation": 0.88
}
```

---

## Próximos Pasos: Integración de Modelos Reales

### Para tu compañero desarrollador de IA

**Archivo:** `backend/ai_services.py`

El código está estructurado en 3 servicios que reemplazan los mocks:

1. **PathDetectionServiceImpl** (~línea 50)
   - Cargar tu modelo de detección de pose
   - Input: ruta del video
   - Output: keypoints, confianza, tiempo

2. **GlossGeneratorServiceImpl** (~línea 125)
   - Cargar tu modelo recurrente (LSTM/Transformer)
   - Input: keypoints del frame anterior
   - Output: glosa, confianza, tiempo

3. **TextTranslationServiceImpl** (~línea 205)
   - Cargar tu modelo generador de texto (T5/LLM)
   - Input: glosa en texto
   - Output: traducción en español, confianza, tiempo

**Instrucciones detalladas:** Ver `API_DOCUMENTATION.md`

---

## Deployment a AWS

### Configuración para producción

```bash
# 1. Usar .env.production en lugar de .env.local
cp .env.local .env.production
# Editar .env.production para AWS

# 2. Instalar dependencias de producción
pip install -r requirements-prod.txt

# 3. Usar Gunicorn para múltiples workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Stack recomendado para AWS:**
- EC2: t3.micro (primer año gratis con AWS Academy)
- RDS: (opcional, para almacenar históricos)
- S3: Almacenamiento de videos
- CloudFront: CDN para servir contenido

---

## Troubleshooting

### Backend

| Error | Solución |
|-------|----------|
| `No module named 'mediapipe'` | Normal en Python 3.13. No tiene wheel oficial. |
| `Address already in use :8000` | Otro proceso usa el puerto. Cambiar en .env o matar proceso. |
| `Form data requires python-multipart` | `pip install python-multipart` |
| `getaddrinfo failed` | Problema de red/DNS. Verificar internet. |

### Mobile

| Error | Solución |
|-------|----------|
| `Connection refused` | Verificar que backend corre en `http://localhost:8000` |
| `Permission denied (cámara)` | Otorgar permisos en Settings → Privacy → Camera |
| `No device found` | Verificar emulador está corriendo o dispositivo conectado |

---

## Estructura de Commits (Git)

```
git add .
git commit -m "feat: backend API con pipeline MOCK - listo para integrar modelos"
git push origin main
```

---

## Contacto & Notas

- Backend Python 3.13 + FastAPI (Uvicorn)
- Mobile Flutter (Android/iOS)
- Pipeline de 3 modelos en paralelo
- Actualmente usando MOCK, listo para modelos reales
- Todo documentado en `API_DOCUMENTATION.md`

---

**Versión:** 1.0.0  
**Última actualización:** 2025-11-16  
**Estado:** ✅ Backend listo para testing / ⏳ Modelos pendientes
