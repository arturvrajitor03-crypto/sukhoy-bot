import os, requests
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

def send(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"SEND ERROR {e}")

@app.route('/')
def home():
    return f"BOT OK Token={bool(TOKEN)} SIMPLE MODE"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print(f"GOT {data}", flush=True)
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            if text == "/start":
                send(chat_id, "Бот живой! ✅\nНаконец-то работает! Пиши /dry")
            elif text.startswith("/dry"):
                send(chat_id, "Принял /dry ✅\nСухой режим включен!")
            else:
                send(chat_id, f"Ты написал: {text}\nКоманды: /start /dry")
    except Exception as e:
        print(f"WEBHOOK ERROR {e}", flush=True)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
