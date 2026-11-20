import os
from flask import Flask, request
import requests

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=data)

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            keyboard = {"inline_keyboard": [[{"text": "🔥 Попробуйте Бесплатно", "callback_data": "try_free"}]]}
            send_message(chat_id, "<b>НОВЫЙ БОТ ДЛЯ ПРОБИВА</b>\n\nНажми кнопку ниже 👇", keyboard)
    if "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        send_message(chat_id, "Бесплатная проба активирована ✅")
    return "OK", 200

@app.route('/setwebhook')
def set_webhook():
    url = "https://sukhoy-bot.onrender.com/webhook"
    r = requests.get(f"{API_URL}/setWebhook", params={"url": url})
    return f"Webhook set: {r.json()}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
