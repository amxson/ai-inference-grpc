import os
import time

try:
    from google import genai
except ImportError:
    genai = None


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def gemini_available() -> bool:
    return genai is not None and bool(os.getenv("GEMINI_API_KEY"))


def call_gemini(prompt: str) -> str:
    """
    Calls Gemini if GEMINI_API_KEY is available.
    Falls back to mock response if Gemini is not configured or fails.
    """
    if not gemini_available():
        return ""

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text or ""
    except Exception as error:
        print(f"[Gemini fallback] Gemini call failed: {error}")
        return ""


def analyze_sentiment(text: str):
    prompt = f"""
Classify the sentiment of the following text as POSITIVE, NEGATIVE, or NEUTRAL.
Return only one label and one confidence score between 0 and 1.

Text: {text}

Format:
LABEL,confidence
Example:
POSITIVE,0.95
"""

    gemini_result = call_gemini(prompt)

    if gemini_result:
        try:
            cleaned = gemini_result.strip().replace("\n", "")
            label, confidence = cleaned.split(",", 1)
            return label.strip().upper(), float(confidence.strip())
        except Exception:
            pass

    # Mock fallback
    text_lower = text.lower()

    positive_words = ["good", "great", "amazing", "excellent", "love", "happy"]
    negative_words = ["bad", "terrible", "poor", "hate", "sad", "awful"]

    if any(word in text_lower for word in positive_words):
        return "POSITIVE", 0.95

    if any(word in text_lower for word in negative_words):
        return "NEGATIVE", 0.90

    return "NEUTRAL", 0.70


def generate_text(prompt: str):
    gemini_result = call_gemini(
        f"Generate a clear short answer for this prompt:\n{prompt}"
    )

    if gemini_result:
        response = gemini_result
    else:
        response = f"This is a simulated AI response for your prompt: {prompt}"

    for token in response.split():
        time.sleep(0.2)
        yield token + " "


def summarize_text(full_text: str):
    gemini_result = call_gemini(
        f"Summarize the following text clearly and briefly:\n\n{full_text}"
    )

    if gemini_result:
        return gemini_result.strip()

    # Mock fallback
    words = full_text.split()

    if len(words) <= 20:
        return full_text

    return " ".join(words[:20]) + "..."


def chat_response(message: str):
    gemini_result = call_gemini(
        f"You are a helpful AI assistant. Reply briefly to this message:\n{message}"
    )

    if gemini_result:
        return gemini_result.strip()

    return f"AI Assistant received your message: {message}"