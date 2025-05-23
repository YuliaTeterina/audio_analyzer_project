from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

emotions = ['негативный', 'нейтральный', 'позитивный']

model_name = "cointegrated/rubert-tiny-sentiment-balanced"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def get_word_sentiment(word):
    inputs = tokenizer(word, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    proba = torch.softmax(outputs.logits, dim=1).numpy()[0]
    return emotions[np.argmax(proba)]