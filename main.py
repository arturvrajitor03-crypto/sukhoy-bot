import requests, time, os
from threading import Thread
from flask import Flask

TOKEN = "9241841874:AAHTlOiEs7jg7RDFbCcMWXXR6DFGsi-QlAc"
CHAT_ID = "123456789"  # ЗАМЕНИ ЭТО НА СВОЙ ID ОТ @userinfobot

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT RABOTAET OK"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
time.sleep(2)

def send(text):
    try:
        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print("TG SEND OK", flush=True)
    except Exception as e:
        print("TG ERR", e, flush=True)

print("=== BOT ZAPUSTILSYA V38 ===", flush=True)
send("TEST BOT ZAPUSTILSYA - PROVERKA")

while True:
    try:
        url = "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUUSD&interval=15&limit=100"
        data = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in data['result']['list']][::-1]
        price = closes[-1]
        ma7 = sum(closes[-7:])/7
        print("Price %.2f MA7 %.2f" % (price, ma7), flush=True)
        if price > ma7:
            send("BUY 85pct XAUUSD %.2f above MA7" % price)
    except Exception as e:
        print("ERR", e, flush=True)
    time.sleep(60)
