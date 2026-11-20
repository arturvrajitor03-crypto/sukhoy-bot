import os, requests, threading, time
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

# активные сигналы: {chat_id: {вход, стоп, цели, направление}}
active = {}

def send(chat_id, text):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except: pass

def get_price():
    try:
        # цена золота
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10).json()
        return float(r['items'][0]['curr'] + r['items'][0]['xauPrice'])
    except:
        return None

def get_signal():
    price = get_price()
    if not price: return None
    # простая логика RSI-подобная для примера
    import random
    # берем из цены - если последняя цифра четная SELL, нечет BUY (для теста логики)
    # в реальном боте тут твоя старая логика RSI
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
                    msg = f"✅ ЦЕЛЬ 1 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp1']}\nЗакрывай часть сделки!"
                elif price <= s['tp2'] and s.get('tp1_done') and not s.get('tp2_done'):
                    s['tp2_done'] = True
                    msg = f"✅✅ ЦЕЛЬ 2 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp2']}"
                elif price <= s['tp3'] and s.get('tp2_done') and not s.get('tp3_done'):
                    msg = f"✅✅✅ ЦЕЛЬ 3 ПРОШЛА! ВСЕ ЦЕЛИ ВЗЯТЫ!\nЦена: {price}"
                    done = True
                elif price >= s['sl']:
                    msg = f"❌ СТОП СРАБОТАЛ\nЦена: {price}\nСтоп был: {s['sl']}"
                    done = True
            else: # BUY
                if price >= s['tp1'] and not s.get('tp1_done'):
                    s['tp1_done'] = True
                    msg = f"✅ ЦЕЛЬ 1 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp1']}\nЗакрывай часть сделки!"
                elif price >= s['tp2'] and s.get('tp1_done') and not s.get('tp2_done'):
                    s['tp2_done'] = True
                    msg = f"✅✅ ЦЕЛЬ 2 ПРОШЛА!\nЦена: {price}\nЦель была: {s['tp2']
