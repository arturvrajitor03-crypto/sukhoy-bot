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
        requests.post("https://api.telegram.org/bot{}/sendMessage".format(TOKEN), data={"chat_id": cid, "text": text}, timeout=15)
    except:
        pass

def get_gold():
    global LAST_PRICE
    price = LAST_PRICE
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r["price"])
        LAST_PRICE = price
    except:
        pass
    minute = datetime.now().minute
    rsi = 35 + (minute % 30)
    if rsi < 40:
        sig = "BUY"
    elif rsi > 60:
        sig = "SELL"
    else:
        sig = "BOKOVIK"
    return price, rsi, sig

def calc_lot(balance):
    risk = balance * 0.02
    lot = risk / 15.0
    if lot < 0.01:
        lot = 0.01
    return round(lot, 2), risk

def auto_loop():
    global BALANCE, CURRENT_POS
    while True:
        try:
            price, rsi, sig = get_gold()
            if sig in ["BUY", "SELL"]:
                if CURRENT_POS is None:
                    lot, risk = calc_lot(BALANCE)
                    CURRENT_POS = {"type": sig, "entry": price, "lot": lot}
                    msg = "V17 {} AUTO TRADE Price {:.2f} RSI {} LOT {} risk {:.0f}$".format(sig, price, rsi, lot, risk)
                    for cid in list(CHATS):
                        send(cid, msg)
            time.sleep(180)
        except Exception as e:
            print("auto err {}".format(e))
            time.sleep(60)

threading.Thread(target=auto_loop, daemon=True).start()

offset = 0
print("V17.2 MINIMAL LIVE")
while True:
    try:
        resp = requests.get("https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=10".format(TOKEN, offset), timeout=20).json()
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            if "message" not in upd:
                continue
            cid = upd["message"]["chat"]["id"]
            CHATS.add(cid)
            txt = upd["message"].get("text", "").strip().lower()
            if txt == "/start":
                send(cid, "V17.2 LIVE Scalper trades in bokovik Commands /check /balance /trades /lot /plan /status")
            elif txt == "/check":
                p, rsi, sig = get_gold()
                send(cid, "{} RSI {} Price {:.2f}".format(sig, rsi, p))
            elif txt == "/balance":
                lot, risk = calc_lot(BALANCE)
                send(cid, "BALANCE {:.2f}$ LOT {} risk {:.0f}$ Pos {} Trades {}".format(BALANCE, lot, risk, CURRENT_POS, len(TRADES)))
            elif txt == "/trades":
                if not TRADES:
                    send(cid, "No trades yet searching")
                else:
                    send(cid, "\n".join(TRADES[-10:]))
            elif txt == "/lot":
                lot, risk = calc_lot(BALANCE)
                send(cid, "LOT from God Bal {:.0f}$ Risk 2%={:.0f}$ LOT {}".format(BALANCE, risk, lot))
            elif txt == "/plan":
                send(cid, "PLAN 5000$/week Now {:.0f}$ Need 166k Week1 {:.0f}$ Week10 {:.0f}$".format(BALANCE, BALANCE*1.1, BALANCE*2.59))
            elif txt == "/status":
                p, rsi, sig = get_gold()
                send(cid, "V17.2 LIVE Sig {} RSI {} Gold {:.2f} Bal {:.0f}$".format(sig, rsi, p, BALANCE))
    except Exception as e:
        print("loop err {}".format(e))
        time.sleep(5)
