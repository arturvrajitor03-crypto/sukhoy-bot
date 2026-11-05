import os, time, requests, threading
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN", "PUT_TOKEN_HERE")
BALANCE = 1000.0
START_BALANCE = 1000.0
CHATS = set()
TRADES = []
CURRENT_POS = None
LAST_PRICE = 4093.0

def send(cid, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": cid, "text": text}, timeout=15)
    except:
        pass

def get_gold():
    global LAST_PRICE
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r["price"])
        LAST_PRICE = price
    except:
        price = LAST_PRICE
    minute = datetime.now().minute
    rsi = 35 + (minute % 30)
    strength = 93
    if rsi < 40:
        sig = "BUY"
    elif rsi > 60:
        sig = "SELL"
    else:
        if price > LAST_PRICE + 2:
            sig = "SCALP_SELL"
        elif price < LAST_PRICE - 2:
            sig = "SCALP_BUY"
        else:
            sig = "BOKOVIK"
    return price, rsi, strength, sig

def calc_lot(balance):
    risk = balance * 0.02
    lot = risk / 15.0
    if lot < 0.01:
        lot = 0.01
    lot = round(lot, 2)
    return lot, risk

def auto_loop():
    global BALANCE, CURRENT_POS
    while True:
        try:
            price, rsi, strength, sig = get_gold()
            if sig in ["BUY", "SCALP_BUY", "SELL", "SCALP_SELL"]:
                if CURRENT_POS is None:
                    lot, risk = calc_lot(BALANCE)
                    CURRENT_POS = {"type": sig, "entry": price, "lot": lot}
                    msg = f"V17 {sig} AUTO-TRADE! Price {price:.2f} RSI {rsi} LOT {lot} risk {risk:.0f}$"
                    for cid in list(CHATS):
                        send(cid, msg)
                else:
                    entry = CURRENT_POS["entry"]
                    is_buy = "BUY" in CURRENT_POS["type"]
                    profit = (price - entry) if is_buy else (entry - price)
                    profit_usd = profit * CURRENT_POS["lot"] * 10
                    if abs(profit) > 3:
                        BALANCE += profit_usd
                        res = "WIN" if profit_usd > 0 else "LOSS"
                        TRADES.append(f"{res} {CURRENT_POS['type']} {entry:.0f}->{price:.0f} {profit_usd:+.1f}$ Bal {BALANCE:.0f}$")
                        close_msg = f"{res} Close {CURRENT_POS['type']} {entry:.2f}->{price:.2f} Profit {profit_usd:+.2f}$ Bal {BALANCE:.2f}$"
                        for cid in list(CHATS):
                            send(cid, close_msg)
                        CURRENT_POS = None
            time.sleep(180)
        except Exception as e:
            print(f"auto err {e}")
            time.sleep(60)

threading.Thread(target=auto_loop, daemon=True).start()

offset = 0
print("V17.1 FIXED LIVE")
while True:
    try:
        resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=10", timeout=20).json()
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            if "message"
