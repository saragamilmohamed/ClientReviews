
import os
import requests
import gspread
from ReviewAnalaysis import analyze_sentiment, sheet, client_twilio
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from flask import Flask, request, jsonify
from pyngrok import ngrok
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# ========== CONFIGURATION ==========
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")


app = Flask(__name__)

@app.route("/webhook/reviews", methods=["POST"])
def receive_review():
    data = request.json or {}
    name = data.get("name")
    product = data.get("product")
    review = data.get("review")

    sentiment = analyze_sentiment(review)
    sheet.append_row([name, product, review, sentiment])

    if "Negative" in sentiment:
        print("🚨 Negative review detected → sending WhatsApp message...")
        message_body = f"⚠️ Negative Review Alert!\n\nProduct: {product}\nClient: {name}\nReview: {review}"
        msg = client_twilio.messages.create(
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP,
            body=message_body
        )
        print(f"✅ Message SID: {msg.sid}")

    return {"status": "success", "sentiment": sentiment}, 200