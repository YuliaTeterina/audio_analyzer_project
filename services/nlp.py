from textblob import TextBlob

emotion_colors = {
    "радость": "#FFD700",
    "грусть": "#4682B4",
    "гнев": "#FF4500",
    "страх": "#800080",
    "нейтрально": "#C0C0C0"
}

def analyze_emotion(word):
    blob = TextBlob(word)
    sentiment = blob.sentiment.polarity
    print(word, sentiment)
    
    if sentiment > 0.3:
        return "радость"
    elif sentiment < -0.3:
        return "гнев"
    else:
        return "нейтрально"

def colorize_text(text):
    words = text.split()
    colored_text = []
    for word in words:
        emotion = analyze_emotion(word)
        color = emotion_colors.get(emotion, "#C0C0C0")
        colored_text.append(f'<span style="color:{color}">{word}</span>')
    return " ".join(colored_text)