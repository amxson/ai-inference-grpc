import time


def analyze_sentiment(text: str):
    text_lower = text.lower()

    positive_words = ["good", "great", "amazing", "excellent", "love", "happy"]
    negative_words = ["bad", "terrible", "poor", "hate", "sad", "awful"]

    if any(word in text_lower for word in positive_words):
        return "POSITIVE", 0.95

    if any(word in text_lower for word in negative_words):
        return "NEGATIVE", 0.90

    return "NEUTRAL", 0.70


def generate_text(prompt: str):
    response = f"This is a simulated AI response for your prompt: {prompt}"
    for token in response.split():
        time.sleep(0.2)
        yield token + " "


def summarize_text(full_text: str):
    words = full_text.split()

    if len(words) <= 20:
        return full_text

    return " ".join(words[:20]) + "..."


def chat_response(message: str):
    return f"AI Assistant received your message: {message}"