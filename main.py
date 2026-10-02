import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")


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

    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()

    result = response.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]


@app.route("/", methods=["GET"])
def home():
    if RENDER_URL:
        try:
            webhook_url = f"{RENDER_URL}/webhook"

            response = requests.post(
                f"{TELEGRAM_URL}/setWebhook",
                json={"url": webhook_url},
                timeout=10
            )

            print("Webhook:", response.text)

        except Exception as e:
            print("Webhook error:", e)

    return "Bot ishlayapti!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    message = update.get("message") or {}
    chat = message.get("chat") or {}
    text = message.get("text")

    if not text or not chat.get("id"):
        return "OK"

    chat_id = chat["id"]

    try:
        answer = ask_gemini(text)

        requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer[:4000]
            },
            timeout=15
        )

    except Exception as e:
        print("ERROR:", e)

    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
