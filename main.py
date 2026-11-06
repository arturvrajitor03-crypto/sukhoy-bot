import requests, time, os
from threading import Thread
from flask import Flask

# ТВОЙ ТОКЕН УЖЕ ВСТАВЛЕН!
TOKEN = "9241841874:AAHTlOiEs7jg7RDFbCcMWXXR6DFGsi-QlAc"
CHAT_ID = "СЮДА_ВСТАВЬ_ID_ОТ_USERINFOBOT"  # <-- сюда вставь ID от @userinfobot

app = Flask(__name__)
@app.route('/')
def home(): 
    return "BOT V38 RABOTAET - Цена 4064 - Все ок!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
time.sleep(2)

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"TG отправил: {text[:30]}", flush=True)
    except Exception as e:
        print(f"TG ошибка: {e}", flush=True)

print("=== BOT ZAPUSTILSYA V38 ===", flush=True)

# Пытаемся отправить тест - если CHAT_ID верный, придет сообщение
try:
    send("✅ БОТ ЗАПУСТИЛСЯ! Тест с токеном 9241841874 - Я РАБОТАЮ!")
except:
    pass

while True:
    try:
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

        print(f"{time.strftime('%H:%M:%S')} Цена {price:.2f} MA7 {ma7:.2f} RSI {rsi:.1f}", flush=True)

        if price > ma7 and rsi < 78:
            send(f"🟢 BUY 85% X
