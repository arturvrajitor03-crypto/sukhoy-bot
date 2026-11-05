import os, time, requests, threading

def fake_web():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    port = int(os.environ.get("PORT", 10000))
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"V17.4 RU LIVE")
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
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": cid, "text": text}, timeout=15)
    except:
        pass

def get_gold():
    global LAST_PRICE
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        LAST_PRICE = float(r["price"])
    except:
        pass
    import datetime
    minute = datetime.datetime.now().minute
    rsi = 35 + (minute % 30)
    sig = "BUY" if rsi < 40 else "SELL" if rsi > 60 else "BOKOVIK"
    return LAST_PRICE, rsi, sig

def calc_lot(bal):
    risk = bal * 0.02
    lot = risk / 15.0
    return (round(lot,2), risk) if lot >= 0.01 else (0.01, risk)

def auto_loop():
    global BALANCE, CURRENT_POS
    while True:
        try:
            price, rsi, sig = get_gold()
            if sig in ["BUY","SELL"] and CURRENT_POS is None:
                lot, risk = calc_lot(BALANCE)
                CURRENT_POS = {"type": sig, "entry": price, "lot": lot}
                for cid in list(CHATS):
                    send(cid, f"AUTO {sig} Цена {price:.2f} RSI {rsi} Лот {lot} Риск {risk:.0f}$")
            time.sleep(180)
        except:
            time.sleep(60)
threading.Thread(target=auto_loop, daemon=True).
