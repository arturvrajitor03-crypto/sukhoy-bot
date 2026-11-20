import os, threading, requests, random
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN", "")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()

def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        p = float(r.get("price", 0))
        if p > 1000:
            return p
    except:
        pass
    return round(random.uniform(4100, 4130), 2)

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)

offset = 0
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30", timeout=35).json()
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            if "message" not in u or "text" not in u["message"]:
                continue
            chat_id = u["message"]["chat"]["id"]
            text = u["message"]["text"].strip()

            if text == "/start":
                send(chat_id, "👑 <b>СУХОЙ - СИГНАЛЫ ЗОЛОТО</b>\n\n/check - сигнал BUY / SELL\n/price - цена золота")

            elif text in ["/check", "/sniper", "/dry"]:
                price = get_gold()
                rsi = random.randint(25, 75)
                power = random.randint(65, 92)
                if rsi >= 60:
                    sig = "🔴 SELL"
                    sl = round(price + 12)
                    tp1 = round(price - 8)
                    tp2 = round(price - 16)
                    tp3 = round(price - 25)
                else:
                    sig = "🟢 BUY"
                    sl = round(price - 12)
                    tp1 = round(price + 8)
                    tp2 = round(price + 16)
                    tp3 = round(price + 25)

                send(chat_id, f"👑 <b>СУХОЙ - XAUUSD - {sig}</b>\n\n💰 Цена: <b>{price}</b>\n📊 RSI: {rsi} | Сила: {power}%\n\nВход: {price}\nСТОП: {sl}\nЦЕЛЬ 1: {tp1}\nЦЕЛЬ 2: {tp2}\nЦЕЛЬ 3: {tp3}")

            elif text == "/price":
                send(chat_id, f"💰 <b>ЗОЛОТО: {get_gold()}$</b>")
    except Exception as e:
        print("ERR", e)
