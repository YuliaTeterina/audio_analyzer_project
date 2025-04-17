from flask import Flask
from config import Config
from celery import Celery
import os


app = Flask(__name__)
app.config.from_object(Config)

# имортируем эндпоинты
from routes import *

# Инициализация Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)