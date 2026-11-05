import os, requests, random, threading, time
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
    return 4077

def send_text(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

def set_webhook():
    time.sleep(4)
    try:
        base_url = os.getenv("RENDER_EXTERNAL_URL")
        if base_url:
            url = f"{base_url}/webhook"
            requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}", timeout=10)
    except:
        pass

threading.Thread(target=set_webhook, daemon=True).start()

@app.route('/')
def home():
    return "SUHOY LIVE - FIXED"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        if "message" not in data or "text" not in data["message"]:
            return "ok"
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()

        if text == "/start":
            send_text(chat_id, "👑 СУХОЙ ЖИВОЙ!\n/dry - сигнал\n/price - цена")
        
        elif text == "/price":
            send_text(chat_id, f"💰 {get_gold_price()}$")
        
        elif text.startswith("/dry"):
            price = get_gold_price()
            if price >= 4050:
                direction = "BUY"
                sl = price - 9
                tp1, tp2, tp3 = price + 4, price + 8, price + 13
            else:
                direction = "SELL"
                sl = price + 9
                tp1, tp2, tp3 = price - 4, price - 8, price - 13
            
            msg = f"👑 {direction} {price}$\nВход: выше {price}\nSL: {sl}\nTP1: {tp1} ⬜\nTP2: {tp2} ⬜\nTP3: {tp3} ⬜"
            send_text(chat_id, msg)
            
    except Exception as e:
        print(e)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
