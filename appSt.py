import os
import requests
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========== CONFIGURATION ==========
import streamlit as st

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
ACCOUNT_SID = st.secrets["ACCOUNT_SID"]
AUTH_TOKEN = st.secrets["AUTH_TOKEN"]
FROM_WHATSAPP = st.secrets["FROM_WHATSAPP"]
TO_WHATSAPP = st.secrets["TO_WHATSAPP"]
NGROK_AUTHTOKEN = st.secrets["NGROK_AUTHTOKEN"]


# ========== GOOGLE SHEETS ==========
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=SCOPE)

client_gs = gspread.authorize(creds)
sheet = client_gs.open("Client Reviews").sheet1

# ========== TWILIO ==========
client_twilio = Client(ACCOUNT_SID, AUTH_TOKEN)

# ========== SENTIMENT FUNCTION ==========
def analyze_sentiment(review):
    prompt = f"""
You are a multilingual sentiment analysis model.
Classify this review as one of: Positive, Negative, or Neutral.
Reply with only one word.

Review: {review}
    """

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        headers={"Content-Type": "application/json"},
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    result = response.json()
    sentiment = (
        result.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )

    return sentiment

# ========== STREAMLIT APP ==========
st.set_page_config(page_title="Client Review Analyzer", page_icon="💬")

st.title("💬 Client Review Sentiment Analyzer")
st.write("Analyze customer feedback and send alerts for negative reviews.")

with st.form("review_form"):
    name = st.text_input("Client Name")
    product = st.text_input("Product Name")
    review = st.text_area("Write the client review")
    submitted = st.form_submit_button("Analyze Review")

if submitted:
    if not review:
        st.error("⚠️ Please enter a review.")
    else:
        sentiment = analyze_sentiment(review)
        st.write(f"**Detected Sentiment:** {sentiment}")

        # Save to Google Sheets
        sheet.append_row([name, product, review, sentiment])

        # If negative, send WhatsApp alert
        if "Negative" in sentiment:
            message_body = f"⚠️ Negative Review Alert!\n\nProduct: {product}\nClient: {name}\nReview: {review}"
            client_twilio.messages.create(
                from_=FROM_WHATSAPP,
                to=TO_WHATSAPP,
                body=message_body
            )
            st.warning("🚨 Negative review detected — WhatsApp alert sent!")

        else:
            st.success("✅ Review saved successfully!")


