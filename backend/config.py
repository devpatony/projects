import os
from pathlib import Path

class Settings:
    # Core Application Settings
    PROJECT_NAME: str = "Excel Processor"
    PROJECT_VERSION: str = "1.1.0"
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_EXTENSIONS: set = {'xlsx', 'xls'}
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_TASK_TIME_LIMIT: int = 600  # 10 minutes
    
    # WebSocket Configuration
    SOCKETIO_MOUNT_LOCATION: str = "/socket.io"
    SOCKETIO_PING_TIMEOUT: int = 30
    SOCKETIO_PING_INTERVAL: int = 5
    
    # Create required directories
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

settings = Settings()