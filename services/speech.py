import os
import wave
import json
from vosk import Model, KaldiRecognizer

def transcribe_audio(model, audio_path):
    #audio_path = r'uploads\audio_20250416_181149.wav'
    #audio_path = 'angry_test.mp3'
    print(audio_path)
    try:
        wf = wave.open(audio_path, "rb")
    except Exception as e:
        print(e)
    rec = KaldiRecognizer(model, wf.getframerate())
    
    result = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part_result = json.loads(rec.Result())
            result.append(part_result.get("text", ""))
    
    final_result = json.loads(rec.FinalResult())
    result.append(final_result.get("text", ""))
    print(result)
    return " ".join(result)