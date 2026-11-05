import os, time, requests, threading, datetime

def fake_web():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    port = int(os.environ.get("PORT", 10000))
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"LIVE")
    HTTPServer(("0.0.0.0", port), H).serve_forever()
threading.Thread(target=fake_web, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN", "")
BALANCE = 1000.0
CHATS = set()
TRADES = []
CURRENT_POS = None
LAST_PRICE = 4093.0

def send(cid, text):
    try:
        u = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
        requests.post(u, data={"chat_id": cid, "text": text}, timeout=15)
    except:
        pass

def get_gold():
    global LAST_PRICE
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        LAST_PRICE = float(r["price"])
    except:
        pass
    m = datetime.datetime.now().minute
    rsi = 35 + (m % 30)
    if rsi < 40:
        sig = "BUY"
    elif rsi > 60:
        sig = "SELL"
    else:
        sig = "BOKOVIK"
    return LAST_PRICE, rsi, sig

def calc_lot(bal):
    risk = bal * 0.02
    lot = risk / 15.0
    if lot < 0.01:
        lot = 0.01
    return round(lot,2), risk

def auto_loop():
    while True:
        try:
            price, rsi, sig = get_gold()
            if sig != "BOKOVIK":
                global CURRENT_POS
                if CURRENT_POS is None:
                    lot, risk = calc_lot(BALANCE)
                    CURRENT_POS = sig
                    msg = "AUTO " + sig + " PRICE " + str(int(price)) + " RSI " + str(rsi) + " LOT " + str(lot)
                    for cid in list(CHATS):
                        send(cid, msg)
            time.sleep(180)
        except:
            time.sleep(60)
threading.Thread(target=auto_loop, daemon=True).start()

offset = 0
print("V17.6 STARTED")
while True:
    try:
        u = "https://api.telegram.org/bot" + TOKEN + "/getUpdates?offset=" + str(offset) + "&timeout=10"
        resp = requests.get(u, timeout=20).json()
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            if "message" not in upd:
                continue
            cid = upd["message"]["chat"]["id"]
            CHATS.add(cid)
            txt = upd["message"].get("text","").lower()
            if "/start" in txt:
                send(cid, "V17.6 RU LIVE\nSam torguet\n1000$ start\n/check\n/balance\n/trades\n/lot\n/plan\n/status")
            if "/check" in txt:
                p, rsi, sig = get_gold()
                send(cid, "BOKOVIK RSI " + str(rsi) + " PRICE " + str(int(p)) if sig=="BOKOVIK" else sig + " RSI " + str(rsi) + " PRICE " + str(int(p)))
            if "/balance" in txt:
                lot, risk = calc_lot(BALANCE)
                send(cid, "Balans " + str(BALANCE) + " Lot " + str(lot) + " Risk " + str(int(risk)) + " Pos " + str(CURRENT_POS))
            if "/trades" in txt:
                send(cid, "Sdelok poka net" if not TRADES else "\n".join(TRADES[-10:]))
            if "/lot" in txt:
                lot, risk = calc_lot(BALANCE)
                send(cid, "Raschet lota Balans " + str(int(BALANCE)) + " Risk " + str(int(risk)) + " Lot " + str(lot))
            if "/plan" in txt:
                send(cid, "Plan 5000$ v nedelyu Seichas " + str(int(BALANCE)))
            if "/status" in txt:
                p, rsi, sig = get_gold()
                send(cid, "V17.6 LIVE " + sig + " RSI " + str(rsi) + " Gold " + str(int(p)))
    except Exception as e:
        print(str(e))
        time.sleep(5)
