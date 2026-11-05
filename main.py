# -*- coding: utf-8 -*-
import threading
from flask import Flask
import os, requests, time
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V11 MAX FIX LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()
TOKEN = os.getenv("BOT_TOKEN")

def get_gold():
    price=None; rsi=44
    try:
        # пробуем 3 раза
        for _ in range(3):
            try:
                r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10, headers={"User-Agent":"Mozilla"}).json()
                if "price" in r:
                    price=float(r["price"])
                    break
            except: time.sleep(1)
        if not price:
            # запасной источник
            r2 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=XAUTUSDT", timeout=10).json()
            if "price" in r2: price=float(r2["price"])
        
        kl = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10, headers={"User-Agent":"Mozilla"}).json()
        if isinstance(kl, list) and len(kl)>20:
            closes=[float(x[4]) for x in kl]
            g=l=0
            for i in range(1,15):
                d=closes[-i]-closes[-i-1]
                g+=d if d>0 else 0
                l+=abs(d) if d<0 else 0
            rs=(g/14)/(l/14 or 1)
            rsi=100-(100/(1+rs))
        
        if price is None: return None,None,"ERR",0
        ema=sum(closes[-20:])/20 if 'closes' in locals() else price
        if rsi<28 and price>ema: return price,rsi,"ПОКУПКА",98
        if rsi<38 and price>ema: return price,rsi,"ПОКУПКА",85
        if rsi>72 and price<ema: return price,rsi,"ПРОДАЖА",98
        if rsi>62 and price<ema: return price,rsi,"ПРОДАЖА",85
        return price,rsi,"БОКОВИК",93
    except Exception as e:
        print(f"gold err {e}")
        return None,None,"ERR",0

def send(cid, t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":cid,"text":t}, timeout=10)
    except: pass

print("V11 STARTED")
off=0
while True:
    try:
        d=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={off}&timeout=20", timeout=25).json()
        for x in d.get("result", []):
            off=x["update_id"]+1
            if "message" not in x: continue
            cid=x["message"]["chat"]["id"]
            txt=(x["message"].get("text","")).strip().lower()
            if txt=="/start":
                send(cid, "СУХОЙ БОТ V11 - МАКСИМУМ 100% FIX\nЗОЛОТО XAUUSD\n/check - сигнал\n/price - цена\n/status")
            elif txt=="/check":
                p,rsi,sig,pw=get_gold()
                if not p: send(cid, "Бинанс глючит, повтори /check через 10 сек")
                elif sig=="ПОКУПКА": send(cid, f"ПОКУПКА Сила {pw}% RSI {int(rsi)} GOLD {p:.2f}")
                elif sig=="ПРОДАЖА": send(cid, f"ПРОДАЖА Сила {pw}% RSI {int(rsi)} GOLD {p:.2f}")
                else: send(cid, f"БОКОВИК {pw}% RSI {int(rsi)} GOLD {p:.2f}")
            elif txt=="/price":
                p,rsi,_,_=get_gold()
                if p: send(cid, f"GOLD {p:.2f} RSI {int(rsi)}")
                else: send(cid, "Бинанс глючит, /price еще раз")
            elif txt=="/status": send(cid, "V11 LIVE - Fix Binance")
    except: time.sleep(3)
