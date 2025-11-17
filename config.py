import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Cargar variables de entorno
env_file = Path(__file__).parent / ".env.local"
load_dotenv(env_file)


class Settings(BaseSettings):
    # Modo aplicación
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Rutas locales
    BASE_DIR: Path = Path(__file__).parent
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads/videos")
    RESULTS_DIR: str = os.getenv("RESULTS_DIR", "./uploads/results")
    
    # Crear directorios si no existen
    @staticmethod
    def ensure_directories():
        os.makedirs("uploads/videos", exist_ok=True)
        os.makedirs("uploads/results", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    # Modelos IA
    PATH_DETECTION_MODEL_PATH: str = os.getenv("PATH_DETECTION_MODEL_PATH", "./models/path_detection_model")
    GLOSS_GENERATOR_MODEL_PATH: str = os.getenv("GLOSS_GENERATOR_MODEL_PATH", "./models/gloss_generator_model")
    TEXT_TRANSLATION_MODEL_PATH: str = os.getenv("TEXT_TRANSLATION_MODEL_PATH", "./models/text_translation_model")
    
    # Configuración de video
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
    MAX_VIDEO_DURATION_SECONDS: int = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "15"))
    VIDEO_RESOLUTION_WIDTH: int = int(os.getenv("VIDEO_RESOLUTION_WIDTH", "1280"))
    VIDEO_RESOLUTION_HEIGHT: int = int(os.getenv("VIDEO_RESOLUTION_HEIGHT", "720"))
    VIDEO_FPS: int = int(os.getenv("VIDEO_FPS", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:8081", "http://localhost:3000", "*"]
    
    # Modelos
    USE_MOCK_MODELS: bool = os.getenv("USE_MOCK_MODELS", "True").lower() == "true"
    MOCK_GLOSS_OUTPUT: str = os.getenv("MOCK_GLOSS_OUTPUT", "CASA TECHO GATO ESTAR-AHÍ")
    MOCK_TRANSLATION_OUTPUT: str = os.getenv("MOCK_TRANSLATION_OUTPUT", "El gato está en el techo de la casa")
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Crear directorios en el inicio
settings.ensure_directories()
