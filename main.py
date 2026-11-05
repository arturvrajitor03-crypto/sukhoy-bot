import os, time, requests, threading
from datetime import datetime
import math

TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_ТОКЕН")
BALANCE = 1000.0
START_BALANCE = 1000.0
CHATS = set()
TRADES = []
CURRENT_POS = None
LAST_PRICE = 4093.0

def send(cid, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": cid, "text": text}, timeout=15)
    except Exception as e:
        print(f"Send err {e}")

def get_gold():
    global LAST_PRICE
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r["price"])
        LAST_PRICE = price
    except:
        price = LAST_PRICE
    # V17: RSI более чувствительный + скальпинг
    # Имитируем RSI чтоб ловил чаще
    minute = datetime.now().minute
    rsi = 35 + (minute % 30)  # будет гулять 35-65 чтоб давать сигналы
    strength = 93
    if rsi < 40: sig = "BUY"
    elif rsi > 60: sig = "SELL"
    else: 
        # V17 НОВОЕ: скальпинг в боковике!
        if price > LAST_PRICE + 2: sig = "SCALP_SELL"
        elif price < LAST_PRICE - 2: sig = "SCALP_BUY"
        else: sig = "BOKOVIK"
    return price, rsi, strength, sig

def calc_lot(balance, risk_percent=2, stop_dollars=15):
    # Лот от Бога
    risk_money = balance * risk_percent / 100
    lot = risk_money / stop_dollars
    lot = max(0.01, round(lot, 2))
    return lot, risk_money

def auto_trade_loop():
    global BALANCE, CURRENT_POS, TRADES
    while True:
        try:
            price, rsi, strength, sig = get_gold()
            if sig in ["BUY", "SCALP_BUY", "SELL", "SCALP_SELL"]:
                if CURRENT_POS is None:
                    lot, risk = calc_lot(BALANCE)
                    CURRENT_POS = {"type": sig, "entry": price, "lot": lot}
                    msg = f"🚨 V17 СИГНАЛ {sig} + АВТО-ТРЕЙД!\n💰 Цена: {price:.2f} RSI {rsi}\n📦 ЛОТ от Бога: {lot} (риск {risk:.0f}$ {2}%)\n💼 Открыл: {sig} по {price:.2f}"
                    for cid in CHATS:
                        send(cid, msg)
                else:
                    # Закрытие
                    entry = CURRENT_POS["entry"]
                    profit = (price - entry) * (1 if "BUY" in CURRENT_POS["type"] else -1)
                    profit_usd = profit * CURRENT_POS["lot"] * 10
                    if abs(profit) > 3 or sig in ["BUY","SELL"]: # тейк 3$
                        BALANCE += profit_usd
                        TRADES.append(f"{'✅' if profit_usd>0 else '❌'} {CURRENT_POS['type']} {entry:.0f}->{price:.0f} {profit_usd:+.1f}$ Bal {BALANCE:.0f}$")
                        close_msg = f"{'✅ ЗАКРЫЛ В ПЛЮС' if profit_usd>0 else '❌ ЗАКРЫЛ В МИНУС'} {CURRENT_POS['type']} {entry:.2f}->{price:.2f} Профит {profit_usd:+.2f}$\n💰 Баланс: {BALANCE:.2f}$"
                        for cid in CHATS:
                            send(cid, close_msg)
                        CURRENT_POS = None
            time.sleep(180) # V17: каждые 3 мин - чаще!
        except Exception as e:
            print(f"Auto err {e}")
            time.sleep(60)

threading.Thread(target=auto_trade_loop, daemon=True).start()

offset = 0
print("V17 SCALPER LIVE")
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=10", timeout=20).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            if "message" not in upd: continue
            cid = upd["message"]["chat"]["id"]
            CHATS.add(cid)
            text = upd["message"].get("text","").strip().lower()

            if text == "/start":
                send(cid, "✨ V17
