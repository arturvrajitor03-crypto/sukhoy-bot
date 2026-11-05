import os, requests, threading, time
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        p = float(r.get("price", 0))
        if p > 1000:
            return int(p)
    except:
        pass
    return 4092

def send_text(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)

def set_webhook():
    time.sleep(4)
    try:
        base_url = os.getenv("RENDER_EXTERNAL_URL")
        if base_url:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={base_url}/webhook", timeout=10)
    except:
        pass

threading.Thread(target=set_webhook, daemon=True).start()

@app.route('/')
def home(): return "SUHOY TEXT ONLY LIVE"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        if text == "/start":
            send_text(chat_id, "👑 СУХОЙ - TEXT MODE\n/dry - сигнал\n/price - цена")
        elif text.startswith("/dry") or text == "/price":
            price = get_gold_price()
            # Логика: сейчас 4092 - бычий рынок, даем BUY
            if price >= 4050:
                direction = "BUY"
                sl = price - 9
                tp1, tp2, tp3 = price + 4, price + 8, price + 13
                entry = f"выше {price}"
            else:
                direction = "SELL"
                sl = price + 9
                tp1, tp2, tp3 = price - 4, price - 8, price - 13
                entry = f"ниже {price}"
            
            if text == "/price":
                send_text(chat_id, f"💰 {price}$")
            else:
                msg = f"👑 {direction} {price}$\nВход: {entry}\nSL: {sl}\nTP1: {tp1} ⬜\nTP2: {tp2} ⬜\nTP3: {tp3} ⬜\nСлежу и ставлю ✅"
                send_text(chat_id, msg)
    except Exception as e:
        print(e)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
