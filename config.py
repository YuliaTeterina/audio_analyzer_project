import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'wav', 'mp3'}
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'