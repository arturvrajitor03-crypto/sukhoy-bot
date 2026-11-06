import requests, time, os
from threading import Thread
from flask import Flask

# === ВСТАВЬ СВОИ ДАННЫЕ СЮДА В КАВЫЧКИ ===
TOKEN = "1234567890:AAH_твой_токен_от_BotFather"
CHAT_ID = "12345678"
# =========================================

app = Flask(__name__)
@app.route('/')
def home():
    return "BOT RABOTAET"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text})
        print(f"Отправил в ТГ: {text}")
    except Exception as e:
        print(f"Ошибка: {e}")

print("=== BOT ZAPUSTILSYA ===")
send("✅ Бот починен! Я работаю! Цена 4064")

while True:
    try:
        # берем цену золота
        url = "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUUSD&interval=15&limit=100"
        data = requests.get(url).json()
        closes = [float(x[4]) for x in data['result']['list']][::-1]
        price = closes[-1]
        ma7 = sum(closes[-7:])/7
        
        # считаем RSI
        gains = losses = 0
        for i in range(-6, 0):
            d = closes[i] - closes[i-1]
            if d > 0: gains += d
            else: losses -= d
        rsi = 100 - (100 / (1 + gains/(losses+0.001)))

        print(f"Цена {price} MA7 {ma7} RSI {rsi}")

        # если сильный BUY 80%+
        if price > ma7 and rsi < 78:
            send(f"🟢 BUY 85% Золото {price:.2f}\nВход сейчас\nSL {price-10:.2f} TP {price+15:.2f}")

    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(300)  # проверка каждые 5 минут
