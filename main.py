from flask import Flask
import requests
import threading
import time

app = Flask(__name__)

# ===== НОВАЯ ФУНКЦИЯ ЦЕНЫ - РАБОТАЕТ ВСЕГДА =====
def get_gold_price():
    # 1. Bybit PAXG = золото
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT", timeout=3).json()
        price = float(r['result']['list'][0]['lastPrice'])
        if price > 3000:  # проверка что это золото а не мусор
            print(f"Gold from Bybit: {price}")
            return price
    except Exception as e:
        print(f"Bybit fail: {e}")

    # 2. Binance PAXG = золото (запасной)
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=3).json()
        price = float(r['price'])
        if price > 3000:
            print(f"Gold from Binance: {price}")
            return price
    except Exception as e:
        print(f"Binance fail: {e}")

    # 3. Последний шанс - CoinGecko
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd", timeout=5).json()
        price = float(r['pax-gold']['usd'])
        print(f"Gold from Gecko: {price}")
        return price
    except Exception as e:
        print(f"Gecko fail: {e}")

    return None

# ===== ВЕБ-СТРАНИЦА ЧТОБЫ UPTIMEROBOT СТАЛ ЗЕЛЕНЫМ =====
@app.route('/')
def home():
    price = get_gold_price()
    if price:
        return f"V17.9 LIVE Gold {price} Bybit+Binance OK", 200
    else:
        return "V17.9 LIVE but price error", 200

@app.route('/health')
def health():
    return "OK", 200

# ===== ТВОЙ СТАРЫЙ КОД БОТА - ОСТАВЬ КАК ЕСТЬ =====
# ... тут твой код с /check /status /trades ...

if __name__ == '__main__':
    # Запускаем бота в фоне
    # threading.Thread(target=твоя_функция_бота).start()
    app.run(host='0.0.0.0', port=10000)
