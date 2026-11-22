import requests, time, threading, os
from flask import Flask

BOT_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"
CHAT_ID = "ВСТАВЬ_СЮДА_СВОЙ_CHAT_ID"

BALANCE = 500.0
TRADES = 0
PNL = 0.0
POSITION = None
SYMBOL = "BTCUSDT"
BINANCE = "https://api.binance.com/api/v3"

# --- Фейковый сайт для Render, чтобы он видел порт ---
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is alive!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web, daemon=True).start()
# ----------------------------------------------------

def send(text):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("send error:", e)

def get_price():
    try:
        r = requests.get(f"{BINANCE}/ticker/price?symbol={SYMBOL}", timeout=10).json()
        return float(r["price"])
    except:
        return 0

def telegram_poll():
    offset = 0
    print("Poll started")
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={"offset": offset, "timeout": 10}, timeout=15).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                txt = u.get("message", {}).get("text", "").strip()
                print("Got:", txt)
                if txt == "/start":
                    send("🤖 Бот работает!\n/balance - баланс\n/price - цена BTC")
                if txt == "/balance":
                    send(f"💰 Баланс: {BALANCE:.1f}$\nСделок: {TRADES}\nPnL: {PNL:.1f}$\nПозиция: {POSITION if POSITION else 'нет'}")
                if txt == "/price":
                    p = get_price()
                    send(f"₿ BTC: {p}$")
        except Exception as e:
            print("poll error:", e)
        time.sleep(2)

def loop():
    while True:
        try:
            price = get_price()
            print(f"Price: {price} Balance: {BALANCE}")
            time.sleep(60)
        except Exception as e:
            print("loop error:", e)
            time.sleep(10)

threading.Thread(target=telegram_poll, daemon=True).start()
threading.Thread(target=loop, daemon=True).start()
print("Bot started!")
while True:
    time.sleep(10)
