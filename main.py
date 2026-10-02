import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def ask_gemini(text):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ]
    }

    r = requests.post(url, json=data, timeout=30)
    result = r.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]


@app.route("/", methods=["GET"])
def home():
    return "Bot ishlayapti!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        try:
            answer = ask_gemini(text)

            requests.post(
                f"{TELEGRAM_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": answer
                }
            )
        except Exception as e:
            print("ERROR:", e)

    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
