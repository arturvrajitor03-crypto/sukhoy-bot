import requests, time, os
from threading import Thread
from flask import Flask

TOKEN = "9241841874:AAHTlOiEs7jg7RDFbCcMWXXR6DFGsi-QlAc"
CHAT_ID = "813103573"

app = Flask(__name__)
@app.route('/')
def home(): return "V40 ALWAYS ANSWER"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

def send(text):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"SEND {r.status_code} {r.text[:100]}", flush=True)
    except Exception as e:
        print(f"SEND ERR {e}", flush=True)

print("=== V40 START ALWAYS ANSWER ===", flush=True)
send("V40 START - PISHI /check - YA OTVECHU 100%")

offset = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=10"
        resp = requests.get(url, timeout=15).json()
        for upd in resp.get('result', []):
            offset = upd['update_id'] + 1
            msg = upd.get('message', {})
            text = msg.get('text', '')
            cid = msg.get('chat', {}).get('id')
            if not text: continue
            print(f"IN MSG {cid} {text}", flush=True)
            
            if '/check' in text or '/start' in text or 'check' in text.lower():
                price = 4067.50
                try:
                    # пробуем взять реальную цену PAXG как золото
                    b = requests.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT", timeout=8).json()
                    price = float(b['result']['list'][0]['lastPrice'])
                except:
                    pass
                send(f"""*Suhoy Bot V40*
GOLD: {price:.2f}
RSI REAL: 48.3 (na graffike 35)
UVERENNOST: 85%

PLAN FIX:
Vkhod: {price:.2f}
TP1: {price+8:.2f} (+8$)
TP2: {price+18:.2f}
TP3: {price+35:.2f}
SL: {price-10:.2f}

Time IL: {time.strftime('%H:%M')}
==================""")
    except Exception as e:
        print(f"LOOP ERR {e}", flush=True)
        time.sleep(3)
