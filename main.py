import requests, time, threading, os
from flask import Flask

# ===== МЕНЯЙ ТОЛЬКО ЭТИ 2 СТРОЧКИ =====
# Сотри всё что в кавычках и вставь свой токен из @BotFather
BOT_TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
# Сотри всё что в кавычках и вставь свой CHAT_ID
CHAT_ID = "8131803573"
# ======================================

BALANCE = 500.0
TRADES = 0
PNL = 0.0
POSITION = None
SYMBOL = "BTCUSDT"
BINANCE = "https://api.binance.com/api/v3"

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

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
                    send(f"💰 Баланс: {BALANCE:.1f}$\nСделок: {TRADES}\nPnL: {PNL:.1f}$")
                if txt == "/price":
                    p = get_price()
                    send(f"₿ BTC: {
