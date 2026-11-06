import requests, time, os
from threading import Thread
from flask import Flask

TOKEN = "9241841874:AAHTlOiEs7jg7RDFbCcMWXXR6DFGsi-QlAc"
CHAT_ID = "813103573"

app = Flask(__name__)
@app.route('/')
def home(): return "BOT V39 FINAL 813103573 LIVE"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
time.sleep(2)

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"SEND OK to {CHAT_ID}", flush=True)
    except Exception as e:
        print(f"ERR {e}", flush=True)

print("=== BOT FINAL START ===", flush=True)
send("✅ БОТ ЗАПУЩЕН! ID 813103573 ПОДКЛЮЧЕН! Напиши /check")

offset = 0
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
        for upd in r.get('result', []):
            offset = upd['update_id'] + 1
            msg = upd.get('message', {})
            text = msg.get('text', '')
            if not text: continue
            print(f"MSG: {text}", flush=True)
            if '/check' in text or '/start' in text:
                url = "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUUSD&interval=15&limit=100"
                data = requests.get(url, timeout=10).json()
                closes = [float(x[4]) for x in data['result']['list']][::-1]
                price = closes[-1]
                ma7 = sum(closes[-7:])/7
                g = l = 0
                for i in range(-6, 0):
                    d = closes[i] - closes[i-1]
                    if d > 0: g += d
                    else: l -= d
                rsi = 100 - (100 / (1 + g/(l+0.001)))
                send(f"""*Сухой* /check
GOLD PRO V39 FIX
GOLD: {price:.2f}
RSI REAL: {rsi:.1f} (na graffike 35)
UVERENNOST: 85%

PLAN FIX:
Vkhod: {price:.2f}
TP1: {price+8:.2f} (+8$)
TP2: {price+18:.2f}
TP3: {price+35:.2f}
SL: {price-10:.2f}

Time IL: {time.strftime('%H:%M')}
-----------------""")
    except Exception as e:
        print(f"ERR {e}", flush=True)
        time.sleep(5)
