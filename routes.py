from flask import render_template, request, jsonify, send_from_directory
import os
from services.speech import transcribe_audio
from services.export import export_to_pdf
from app import app, celery
from vosk import Model
from datetime import datetime
import time
from pydub import AudioSegment
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

MODEL_NAME = "vosk-model-small-ru-0.22"

if not os.path.exists(MODEL_NAME):
    raise FileNotFoundError("Модель Vosk не найдена")
else:
    model = Model(MODEL_NAME)
    print('Модель Vosk успешно инициализирована!')

emotions = ['negative', 'neutral', 'positive']

# Загружаем модель при старте сервера
model_name = "cointegrated/rubert-tiny-sentiment-balanced"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


@app.route('/')
def index():
    print('INDEX HTML')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не выбран"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Пустое имя файла"}), 400
    
    if file and file.filename.split('.')[-1] in app.config['ALLOWED_EXTENSIONS']:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Синхронная обработка (для коротких файлов)
        text = transcribe_audio(model, filename)
        colored_text = colorize_text(text)
        return jsonify({"text": text, "colored_text": colored_text})
    
    return jsonify({"error": "Недопустимый формат файла"}), 400


@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "Нет текста для экспорта"}), 400
    
    export_to_pdf(text)
    return send_from_directory('.', 'result.pdf', as_attachment=True)

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    text = request.json.get('text', '')
    
    words = list(set(word.strip(".,!?") for word in text.split() if word.strip(".,!?")))
    
    results = []
    for word in words:
        inputs = tokenizer(word, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        proba = torch.softmax(outputs.logits, dim=1).numpy()[0]
        sentiment = ['negative', 'neutral', 'positive'][np.argmax(proba)]
        results.append({
            'word': word,
            'sentiment': sentiment,
            'confidence': float(np.max(proba))
        })

    return jsonify(results)