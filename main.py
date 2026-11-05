# -*- coding: utf-8 -*-
import threading
from flask import Flask
import os, requests, time
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V13 BEAUTIFUL MAX LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()
TOKEN = os.getenv("BOT_TOKEN")

def get_gold():
    try:
        base="https://data-api.binance.vision"
        r=requests.get(f"{base}/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price=float(r["price"])
        kl=requests.get(f"{base}/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes=[float(x[4]) for x in kl]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            g+=d if d>0 else 0
            l+=abs(d) if d<0 else 0
        rs=(g/14)/(l/14 or 1)
        rsi=100-(100/(1+rs))
        ema=sum(closes[-20:])/20
        if rsi<28 and price>ema: return price,rsi,"ПОКУПКА",98
        if rsi<38 and price>ema: return price,rsi,"ПОКУПКА",85
        if rsi>72 and price<ema: return price,rsi,"ПРОДАЖА",98
        if rsi>62 and price<ema: return price,rsi,"ПРОДАЖА",85
        return price,rsi,"БОКОВИК",93
    except: return None,None,"ERR",0

def send(cid,t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":cid,"text":t}, timeout=10)
    except: pass

print("V13 BEAUTIFUL STARTED")
off=0
while True:
    try:
        d=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={off}&timeout=20", timeout=25).json()
        for x in d.get("result",[]):
            off=x["update_id"]+1
            if "message" not in x: continue
            cid=x["message"]["chat"]["id"]
            txt=(x["message"].get("text","")).strip().lower()
            if txt=="/start":
                send(cid,"✨ СУХОЙ БОТ V13 BEAUTIFUL MAX ✨\n🏆 ЗОЛОТО XAUUSD - ТОЛЬКО НА РУССКОМ\n\n📊 /check - сигнал\n💰 /price - цена\n⚙️ /status - статус")
            elif txt=="/check":
                p,rsi,sig,pw=get_gold()
                if not p: send(cid,"⏳ Бинанс думает, нажми /check через 5 сек")
                elif sig=="ПОКУПКА":
                    send(cid,f"🟢 ПОКУПКА\n🔥 Сила: {pw}%\n📈 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n✅ Можно брать лонг!")
                elif sig=="ПРОДАЖА":
                    send(cid,f"🔴 ПРОДАЖА\n🔥 Сила: {pw}%\n📉 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n✅ Можно брать шорт!")
                else:
                    send(cid,f"⏳ БОКОВИК\n⚪ Сила: {pw}%\n📊 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n⏸ Ждем сигнал...")
            elif txt=="/price":
                p,rsi,_,_=get_gold()
                if p: send(cid,f"💰 ЗОЛОТО XAUUSD\n💵 Цена: {p:.2f}$\n📊 RSI: {int(rsi)}")
            elif txt=="/status": send(cid,"✅ V13 BEAUTIFUL LIVE\n🟢 Работает 24/7\n💎 data-api.binance.vision\n🚀 МАКСИМУМ 100%")
    except: time.sleep(3)
