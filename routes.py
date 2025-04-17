from flask import render_template, request, jsonify, send_from_directory
import os
from services.speech import transcribe_audio
from services.nlp import colorize_text
from services.export import export_to_pdf
from tasks.tasks import process_audio
from app import app, celery
from vosk import Model
from datetime import datetime
import time
from pydub import AudioSegment

MODEL_NAME = "vosk-model-small-ru-0.22"

if not os.path.exists(MODEL_NAME):
    raise FileNotFoundError("Модель Vosk не найдена")
else:
    model = Model(MODEL_NAME)
    print('Модель Vosk успешно инициализирована!')

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

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    #time.sleep(1)
    
    audio_file = request.files['audio']

    #audio_file = 'record_out.wav'
    
    try:
        # Конвертируем в правильный WAV

        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_frame_rate(32000).set_channels(1).set_sample_width(2)
        
        filename = os.path.join(app.config['UPLOAD_FOLDER'], "temp.wav")
        audio.export(filename, format="wav")
        #time.sleep(1)
        
        text = transcribe_audio(model, filename)
        colored_text = colorize_text(text)
        
        return jsonify({
            "text": text,
            "colored_text": colored_text
        })
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/process_async', methods=['POST'])
def process_async():
    file = request.files['file']
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        task = process_audio.delay(filename)  # Асинхронная задача
        return jsonify({"task_id": task.id}), 202

@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "Нет текста для экспорта"}), 400
    
    export_to_pdf(text)
    return send_from_directory('.', 'result.pdf', as_attachment=True)