# -*- coding: utf-8 -*-
import threading
from flask import Flask
import os, requests, time, datetime

# === ФИКС RENDER LIVE ===
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V9 RUSSIAN LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()
# === КОНЕЦ ФИКСА ===

TOKEN = os.getenv("BOT_TOKEN")
AUTO = False
LAST_SIGNAL = "Нет данных"
LAST_PRICE = 0
LAST_RSI = 0
LAST_TIME = ""

def get_gold():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        kl = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(x[4]) for x in kl]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: g+=d
            else: l+=abs(d)
        rs = (g/14)/(l/14) if l!=0 else 100
        rsi = 100 - (100/(1+rs))
        ema = sum(closes[-20:])/20
        
        sig="БОКОВИК"
        power=50
        if rsi<25 and price>ema: 
            sig="ПОКУПКА"; power=95+int((25-rsi)/2)
        elif rsi<35 and price>ema:
            sig="ПОКУПКА"; power=80+int((35-rsi))
        elif rsi>75 and price<ema:
            sig="ПРОДАЖА"; power=95+int((rsi-75)/2)
        elif rsi>65 and price<ema:
            sig="ПРОДАЖА"; power=80+int((rsi-65))
        else:
            sig="БОКОВИК"; power=90-abs(50-int(rsi))

        if power>99: power=99
        if power<50: power=50
        
        return price, rsi, sig, power
    except Exception as e:
        print(f"Error gold: {e}")
        return None, None, "ERROR", 0

def send(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

print("V9 RUSSIAN STARTED")
offset=0
last_auto_check=0

while True:
    try:
        # Авто проверка каждые 5 минут
        if AUTO and time.time()-last_auto_check > 300:
            p,rsi,sig,power = get_gold()
            if p:
                LAST_SIGNAL = sig; LAST_PRICE=p; LAST_RSI=rsi
                LAST_TIME = datetime.datetime.now().strftime("%H:%M")
                # тут можно добавить отправку в чат если нужно
            last_auto_check=time.time()

        up = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
        for u in up.get("result", []):
            offset = u["update_id"]+1
            if "message" not in u: continue
            chat_id = u["message"]["chat"]["id"]
            txt = (u["message"].get("text","")).strip().lower()
            print(f"CMD: {txt}")

            if txt in ["/start", "старт"]:
                send(chat_id, "<b>🇷🇺 СУХОЙ V9 РУССКИЙ - МАКСИМУМ 100%</b>\n\nЗОЛОТО XAUUSD\nБЕЗ РЕКЛАМЫ - ТОЛЬКО НА РУССКОМ\n\n/check - сигнал\n/price - цена\n/status - последн\n/auto on - авто вкл\n/auto off - авто выкл")

            elif txt in ["/check", "чек"]:
                p,rsi,sig,power = get_gold()
                if not p:
                    send(chat_id, "❌ Ошибка Binance, попробуй еще раз /check")
                else:
                    LAST_SIGNAL=sig; LAST_PRICE=p; LAST_RSI=rsi; LAST_TIME=datetime.datetime.now().strftime("%H:%M:%S")
                    if sig=="ПОКУПКА":
                        send(chat_id, f"🟢 <b>ПОКУПКА</b>\nСила {power}%\nRSI {int(rsi)}\nЦена {p:.2f}\nВремя {LAST_TIME}")
                    elif sig=="ПРОДАЖА":
                        send(chat_id, f"🔴 <b>ПРОДАЖА</b>\nСила {power}%\nRSI {int(rsi)}\nЦена {p:.2f}\nВремя {LAST_TIME}")
                    else:
                        send(chat_id, f"⏳ <b>БОКОВИК</b> {power}% RSI {int(rsi)}\nЦена {p:.2f}\nЖдем...")

            elif txt in ["/price", "цена"]:
                p,rsi,sig,power = get_gold()
                if p: send(chat_id, f"💰 ЗОЛОТО: {p:.2f}$\nRSI: {int(rsi)}\n{p}")

            elif txt in ["/status", "статус"]:
                send(chat_id, f"📊 СТАТУС:\nПоследний: {LAST_SIGNAL} {LAST_PRICE:.2f} RSI {int(LAST_RSI)}\nВремя: {LAST_TIME}\nАвто: {'ВКЛ' if AUTO else 'ВЫКЛ'}")

            elif txt in ["/auto on", "/auto_on", "авто вкл", "/autoon"]:
                AUTO=True
                send(chat_id, "✅ АВТО ВКЛ\nБуду проверять
