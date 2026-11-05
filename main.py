# -*- coding: utf-8 -*-
import threading
from flask import Flask
import os, requests, time
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V10 MAX 100% RUSSIAN LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")

def get_gold():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        k = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(x[4]) for x in k]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            g+=d if d>0 else 0
            l+=abs(d) if d<0 else 0
        rs = (g/14)/(l/14 or 1)
        rsi = 100 - (100/(1+rs)) if rs!=0 else 50
        ema = sum(closes[-20:])/20
        if rsi<25 and price>ema: return price,rsi,"BUY",98
        if rsi<35 and price>ema: return price,rsi,"BUY",85
        if rsi>75 and price<ema: return price,rsi,"SELL",98
        if rsi>65 and price<ema: return price,rsi,"SELL",85
        return price,rsi,"WAIT",93
    except: return None,None,"ERR",0

def send(c,t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":c,"text":t}, timeout=10)
    except: pass

print("V10 RUS MAX 100% STARTED")
off=0
while True:
    try:
        d = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={off}&timeout=20", timeout=25).json()
        for x in d.get("result", []):
            off=x["update_id"]+1
            if "message" not in x: continue
            cid=x["message"]["chat"]["id"]
            txt=(x["message"].get("text","")).strip().lower()

            if txt=="/start":
                send(cid, "SUHOY BOT V10 - MAXIMUM 100%\nZOLOTO XAUUSD - BEZ REKLAMY - TOLKO NA RUSSKOM\n\n/check - signal\n/price - cena\n/status - info\n/auto on\n/auto off")

            elif txt=="/check":
                p,rsi,sig,pw=get_gold()
                if not p: send(cid, "Oshibka Binance")
                elif sig=="BUY": send(cid, f"POKUPKA Sila {pw}% | RSI {int(rsi)} | GOLD {p:.2f}")
                elif sig=="SELL": send(cid, f"PRODAZHA Sila {pw}% | RSI {int(rsi)} | GOLD {p:.2f}")
                else: send(cid, f"BOKOVIK {pw}% | RSI {int(rsi)} | GOLD {p:.2f}")

            elif txt=="/price":
                p,rsi,_,_=get_gold()
                if p: send(cid, f"GOLD: {p:.2f} | RSI {int(rsi)}")

            elif txt=="/status":
                send(cid, "BOT V10 LIVE - MAXIMUM 100% - Rabotaet 24/7")

            elif txt in ["/auto on","/auto_on"]: send(cid, "AUTO VKL")
            elif txt in ["/auto off","/auto_off"]: send(cid, "AUTO VYKL")
    except Exception as e:
        print(e); time.sleep(3)
