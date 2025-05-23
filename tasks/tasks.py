from celery import Celery
from services.speech import transcribe_audio
from app import celery

@celery.task
def process_audio(filepath):
    text = transcribe_audio(model, filepath)
    colored_text = colorize_text(text)
    return {"text": text, "colored_text": colored_text}