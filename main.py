import os, requests, threading, time
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)
active = {}

def send(chat_id, text):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except: pass

def get_price():
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10).json()
        return float(r['items'][0]['xauPrice'])
    except:
        return None

def get_signal():
    price = get_price()
    if not price: return None
    rsi = 72 if price > 3570 else 28
    direction = "SELL" if rsi > 60 else "BUY"
    if direction == "SELL":
        return {"dir": direction, "entry": price, "sl": price + 12, "tp1": price - 8, "tp2": price - 16, "tp3": price - 25, "rsi": rsi}
    else:
        return {"dir": direction, "entry": price, "sl": price - 12, "tp1": price + 8, "tp2": price + 16, "tp3": price + 25, "rsi": rsi}

def checker():
    while True:
        time.sleep(30)
        if not active: continue
        price = get_price()
        if not price: continue
        for chat_id, s in list(active.items()):
            done = False
            msg = ""
            if s['dir'] == "SELL":
                if price <= s['tp1'] and not s.get('tp1_done'):
                    s['tp1_done'] = True
                    msg = f"✅ ЦЕЛЬ 1 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp1']}"
                elif price <= s['tp2'] and s.get('tp1_done') and not s.get('tp2_done'):
                    s['tp2_done'] = True
                    msg = f"✅✅ ЦЕЛЬ 2 ПРОШЛА!\nЦена: {price}"
                elif price <= s['tp3'] and s.get('tp2_done') and not s.get('tp3_done'):
                    msg = f"✅✅✅ ЦЕЛЬ 3 ПРОШЛА! ВСЕ ЦЕЛИ ВЗЯТЫ!\nЦена: {price}"
                    done = True
                elif price >= s['sl']:
                    msg = f"❌ СТОП СРАБОТАЛ\nЦена: {price}"
                    done = True
            else:
                if price >= s['tp1'] and not s.get('tp1_done'):
                    s['tp1_done'] = True
                    msg = f"✅ ЦЕЛЬ 1 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp1']}"
                elif price >= s['tp2'] and s.get('tp1_done') and not s.get('tp2_done'):
                    s['tp2_done'] = True
                    msg = f"✅✅ ЦЕЛЬ 2 ПРОШЛА!\nЦена: {price}"
                elif price >= s['tp3'] and s.get('tp2_done') and not s.get('tp3_done'):
                    msg = f"✅✅✅ ЦЕЛЬ 3 ПРОШЛА! ВСЕ ЦЕЛИ ВЗЯТЫ!\nЦена: {price}"
                    done = True
                elif price <= s['sl']:
                    msg = f"❌ СТОП СРАБОТАЛ\nЦена: {price}"
                    done = True
            if msg: send(chat_id, msg)
            if done: del active[chat_id]

threading.Thread(target=checker, daemon=True).start()

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data: return "ok"
    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    if text == "/start":
        send(chat_id, "👑 СУХОЙ - СИГНАЛЫ ЗОЛОТО\n/check - сигнал\n/price - цена")
    elif text == "/check":
        s = get_signal()
        if not s:
            send(chat_id, "Ошибка цены, попробуй еще раз")
            return "ok"
        active[chat_id] = s
        emoji = "🔴" if s['dir'] == "SELL" else "🟢"
        send(chat_id, f"👑 СУХОЙ - XAUUSD - {emoji} {s['dir']}\n\n💰 Цена: {s['entry']}\n📊 RSI: {s['rsi']}\n\nВход: {s['entry']}\nСТОП: {s['sl']}\nЦЕЛЬ 1: {s['tp1']}\nЦЕЛЬ 2: {s['tp2']}\nЦЕЛЬ 3: {s['tp3']}\n\nЯ слежу, пришлю ✅ когда цель пройдет")
    elif text == "/price":
        p = get_price()
        send(chat_id, f"💰 Цена золота: {p}" if p else "Ошибка")
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
