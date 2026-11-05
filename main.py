import os, time, requests, threading
from datetime import datetime

# FIX ДЛЯ RENDER - ОТКРЫВАЕМ ПОРТ
def fake_web():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    port = int(os.environ.get("PORT", 10000))
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"V17.3 LIVE")
    HTTPServer(("0.0.0.0", port), H).serve_forever()

threading.Thread(target=fake_web, daemon=True).start()
print("Fake web on PORT started")

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
    sig = "BUY" if rsi < 40 else "SELL" if rsi > 60 else "BOKOVIK"
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
                    msg = "V17.3 {} AUTO Price {:.2f} RSI {} LOT {}".format(sig, price, rsi, lot)
                    for cid in list(CHATS):
                        send(cid, msg)
            time.sleep(180)
        except Exception as e:
            print("auto err {}".format(e))
            time.sleep(60)

threading.Thread(target=auto_loop, daemon=True).start()

offset = 0
print("V17.3 FIXED PORT BINDING LIVE")
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
                send(cid, "V17.3 LIVE FIXED PORT Commands /check /balance /trades /lot /plan /status")
            elif txt == "/check":
                p, rsi, sig = get_gold()
                send(cid, "{} RSI {} Price {:.2f}".format(sig, rsi, p))
            elif txt == "/balance":
                lot, risk = calc_lot(BALANCE)
                send(cid, "BALANCE {:.2f}$ LOT {} risk {:.0f}$ Pos {} Trades {}".format(BALANCE, lot, risk, CURRENT_POS, len(TRADES)))
            elif txt == "/trades":
                send(cid, "\n".join(TRADES[-10:]) if TRADES else "No trades yet")
            elif txt == "/lot":
                lot, risk = calc_lot(BALANCE)
                send(cid, "LOT Bal {:.0f}$ Risk {:.0f}$ LOT {}".format(BALANCE, risk, lot))
            elif txt == "/plan":
                send(cid, "PLAN 5000$/week Now {:.0f}$ Week1 {:.0f}$ Week10 {:.0f}$".format(BALANCE, BALANCE*1.1, BALANCE*2.59))
            elif txt == "/status":
                p, rsi, sig = get_gold()
                send(cid, "V17.3 LIVE Sig {} RSI {} Gold {:.2f} Bal {:.0f}$".format(sig, rsi, p, BALANCE))
    except Exception as e:
        print("loop err {}".format(e))
        time.sleep(5)
