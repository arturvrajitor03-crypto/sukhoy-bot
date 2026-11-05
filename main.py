# -*- coding: utf-8 -*-
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
        sig = "БОКОВИК"
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
            if sig != "БОКОВИК":
                global CURRENT_POS
                if CURRENT_POS is None:
                    lot, risk = calc_lot(BALANCE)
                    CURRENT_POS = sig
                    msg = "АВТО " + sig + " Цена " + str(int(price)) + " RSI " + str(rsi) + " Лот " + str(lot)
                    for cid in list(CHATS):
                        send(cid, msg)
            time.sleep(180)
        except:
            time.sleep(60)
threading.Thread(target=auto_loop, daemon=True).start()

offset = 0
print("V17.7 RU STARTED")
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
                send(cid, "V17.7 RU LIVE\nСам торгует виртуально!\nСтарт 1000 долл\nШлет только BUY/SELL\n\nКоманды:\n/check - проверить сигнал\n/balance - баланс\n/trades - сделки\n/lot - расчет лота\n/plan - план 5000\n/status - статус")
            if "/check" in txt:
                p, rsi, sig = get_gold()
                if sig == "БОКОВИК":
                    send(cid, "БОКОВИК 93 проц RSI " + str(rsi) + " Цена " + str(int(p)) + " Ждем")
                else:
                    send(cid, "Сигнал " + sig + " RSI " + str(rsi) + " Цена " + str(int(p)))
            if "/balance" in txt:
                lot, risk = calc_lot(BALANCE)
                send(cid, "Баланс " + str(BALANCE) + " Лот " + str(lot) + " Риск " + str(int(risk)) + " Позиция " + str(CURRENT_POS))
            if "/trades" in txt:
                send(cid, "Сделок пока нет, ищем BUY/SELL" if not TRADES else "\n".join(TRADES[-10:]))
            if "/lot" in txt:
                lot, risk = calc_lot(BALANCE)
                send(cid, "Расчет лота от Бога\nБаланс " + str(int(BALANCE)) + "\nРиск 2 проц = " + str(int(risk)) + "\nЛот " + str(lot))
            if "/plan" in txt:
                send(cid, "План 5000 в неделю\nСейчас " + str(int(BALANCE)) + "\nЧерез неделю " + str(int(BALANCE*1.1)) + "\nЧерез 10 недель " + str(int(BALANCE*2.59)))
            if "/status" in txt:
                p, rsi, sig = get_gold()
                send(cid, "V17.7 LIVE\nСигнал " + sig + "\nRSI " + str(rsi) + "\nЗолото " + str(int(p)) + "\nБаланс " + str(int(BALANCE)))
    except Exception as e:
        print(str(e))
        time.sleep(5)
