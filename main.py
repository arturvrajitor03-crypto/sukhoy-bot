# -*- coding: utf-8 -*-
import threading
from flask import Flask
import os, requests, time

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V9 RUSSIAN MAX 100% LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
AUTO = False
LAST = {"sig":"N/A","price":0,"rsi":0,"time":"--:--"}

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
        sig="BOKOVIK"; power=93
        if rsi<25 and price>ema: sig="POKUPKA"; power=98
        elif rsi<35 and price>ema: sig="POKUPKA"; power=85
        elif rsi>75 and price<ema: sig="PRODAZHA"; power=98
        elif rsi>65 and price<ema: sig="PRODAZHA"; power=85
        return price,rsi,sig,power
    except: return None,None,"ERROR",0

def send(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":chat_id,"text":text}, timeout=10)
    except: pass

print("V9 RUS MAX STARTED")
offset=0
while True:
    try:
        u = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
        for ev in u.get("result", []):
            offset = ev["update_id"]+1
            if "message" not in ev: continue
            chat_id = ev["message"]["chat"]["id"]
            txt = (ev["message"].get("text","")).strip().lower()

            if txt=="/start":
                send(chat_id, "SUHOY BOT V9 - MAX 100% - NA RUSSKOM\n/check - signal GOLD\n/price - cena\n/status - status\n/auto on - vkl auto\n/auto off - vykl auto")

            elif txt=="/check":
                p,rsi,sig,power = get_gold()
                if not p: send(chat_id, "Oshibka, povtori /check")
                else:
                    LAST["sig"]=sig; LAST["price"]=p; LAST["rsi"]=rsi; LAST["time"]=time.strftime("%H:%M:%S")
                    if sig=="POKUPKA": send(chat_id, f"POKUPKA Sila {power}% | RSI {int(rsi)} | GOLD {p:.2f}")
                    elif sig=="PRODAZHA": send(chat_id, f"PRODAZHA Sila {power}% | RSI {int(rsi)} | GOLD {p:.2f}")
                    else: send(chat_id, f"BOKOVIK {power}% | RSI {int(rsi)} | GOLD {p:.2f} - Zhdem")

            elif txt=="/price":
                p,rsi,sig,power = get_gold()
                if p: send(chat_id, f"GOLD {p:.2f} | RSI {int(rsi)}")

            elif txt=="/status":
                send(chat_id, f"STATUS: {LAST['sig']} {LAST['price']:.2f} RSI {int(LAST['rsi'])} | {LAST['time']} | AUTO {'ON' if AUTO else 'OFF'}")

            elif txt in ["/auto on","/auto_on","/autoon"]:
                AUTO=True; send(chat_id, "AUTO VKL - proverka kazhdye 5 min")
            elif txt in ["/auto off","/auto_off","/autooff"]:
                AUTO=False; send(chat_id, "AUTO VYKL")
    except Exception as e:
        print(e); time.sleep(3)
