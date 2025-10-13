
import os
import requests
import gspread
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from flask import Flask, request, jsonify
from pyngrok import ngrok
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# ========== CONFIGURATION ==========
# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")


# ========== GOOGLE SHEETS ==========

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(
    "genial-wonder-473209-g7-2d1fe8f7d713.json",
    scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open("Client Reviews").sheet1

# ========== TWILIO ==========
client_twilio = Client(ACCOUNT_SID, AUTH_TOKEN)

# ========== GEMINI SENTIMENT ==========
def analyze_sentiment(review):
    prompt = f"""
You are an advanced multilingual sentiment analysis model.
Your task: classify the sentiment of the following review as one of three classes:
1️⃣ Positive – if it expresses satisfaction, happiness, or appreciation.
2️⃣ Negative – if it expresses dissatisfaction, complaint, or anger.
3️⃣ Neutral – if it is balanced, unclear, or neither positive nor negative.

The review may be in English or Arabic.
Reply with **only one exact word**: Positive, Negative, or Neutral.

Examples:
- "The service is great!" → Positive
- "I'm unhappy with the product." → Negative
- "الخدمة ممتازة جدًا شكراً لكم" → Positive
- "التعامل سيء جدًا" → Negative
- "الخدمة عادية" → Neutral

Now analyze this review and answer with only one exact word:
{review}
    """

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        headers={"Content-Type": "application/json"},
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    result = response.json()

    # Safely extract Gemini’s answer
    sentiment = (
        result.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )

    print("🧠 Gemini raw response:", sentiment)
    return sentiment




