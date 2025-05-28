from flask import Flask
from config import Config
from celery import Celery
import os
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# имортируем эндпоинты
from routes import *

# Инициализация Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0",port=5000,debug=True)