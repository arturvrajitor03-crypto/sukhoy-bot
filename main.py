import threading
from flask import Flask
import os, requests, time

# === ФИКС ДЛЯ RENDER - ОТКРЫВАЕМ ПОРТ ===
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "V8 ULTRA LIVE - Bot is running!"
def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()
# === КОНЕЦ ФИКСА ===

TOKEN = os.getenv("BOT_TOKEN")
AUTO = False

def get_signal():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        k = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(x[4]) for x in k]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: g+=d
            else: l+=abs(d)
        rsi = 100 if l==0 else 100-(100/(1+(g/14)/(l/14 or 1)))
        ema = sum(closes[-20:])/20
        sig="WAIT"
        if rsi<32 and price>ema: sig="BUY"
        elif rsi>68 and price<ema: sig="SELL"
        sl = price*0.998 if sig=="BUY" else price*1.002
        tp = price*1.005 if sig=="BUY" else price*0.995
        return price,rsi,sig,sl,tp
    except Exception as e:
        print(f"Signal error: {e}")
        return None,None,"ERROR",0,0

def send(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)
    except: pass

print("V8 ULTRA STARTED - Waiting for commands...")
offset=0
while True:
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
        for u in updates.get("result", []):
            offset = u["update_id"]+1
            if "message" not in u: continue
            chat_id = u["message"]["chat"]["id"]
            txt = u["message"].get("text","")
            print(f"Got: {txt}")
            if txt=="/start":
                send(chat_id, "🤖 V8 ULTRA LIVE!\n\n/check - сигнал GOLD\n/auto_on -
