# -*- coding: utf-8 -*-
import threading, os, requests, time
from flask import Flask
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V14 AUTO BEAUTIFUL MAX LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
CHATS = set() # подписчики

def get_gold():
    try:
        base="https://data-api.binance.vision"
        r=requests.get(f"{base}/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price=float(r["price"])
        kl=requests.get(f"{base}/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=30", timeout=10).json()
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

def auto_sender():
    last_sig=""
    while True:
        time.sleep(2100) # 35 минут
        if not CHATS: continue
        p,rsi,sig,pw=get_gold()
        if not p: continue
        # шлем только если сигнал поменялся или сильный
        if sig=="БОКОВИК" and last_sig=="БОКОВИК": continue
        last_sig=sig
        if sig=="ПОКУПКА":
            txt=f"🔔 АВТО-СИГНАЛ!\n\n🟢 ПОКУПКА\n🔥 Сила: {pw}%\n📈 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n✅ Время брать лонг!"
        elif sig=="ПРОДАЖА":
            txt=f"🔔 АВТО-СИГНАЛ!\n\n🔴 ПРОДАЖА\n🔥 Сила: {pw}%\n📉 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n✅ Время брать шорт!"
        else:
            txt=f"🔔 АВТО-ОБНОВЛЕНИЕ\n\n⏳ БОКОВИК\n⚪ Сила: {pw}%\n📊 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n\n⏸ Ждем..."
        for cid in list(CHATS):
            send(cid,txt)

threading.Thread(target=auto_sender, daemon=True).start()
print("V14 AUTO STARTED")
off=0
while True:
    try:
        d=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={off}&timeout=20", timeout=25).json()
        for x in d.get("result",[]):
            off=x["update_id"]+1
            if "message" not in x: continue
            cid=x["message"]["chat"]["id"]
            CHATS.add(cid)
            txt=(x["message"].get("text","")).strip().lower()
            if txt=="/start":
                send(cid,"✨ СУХОЙ БОТ V14 AUTO MAX ✨\n🏆 ЗОЛОТО XAUUSD\n🔔 АВТО-сигналы каждые 35 мин ВКЛ!\n\n📊 /check - сигнал сейчас\n💰 /price - цена\n⚙️ /status - статус\n🔕 /stop - выкл авто")
            elif txt=="/check":
                p,rsi,sig,pw=get_gold()
                if not p: send(cid,"⏳ Думаю, /check еще раз")
                elif sig=="ПОКУПКА": send(cid,f"🟢 ПОКУПКА\n🔥 Сила: {pw}%\n📈 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}")
                elif sig=="ПРОДАЖА": send(cid,f"🔴 ПРОДАЖА\n🔥 Сила: {pw}%\n📉 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}")
                else: send(cid,f"⏳ БОКОВИК\n⚪ Сила: {pw}%\n📊 RSI: {int(rsi)}\n💰 GOLD: {p:.2f}\n⏸ Ждем сигнал...")
            elif txt=="/price":
                p,rsi,_,_=get_gold()
                if p: send(cid,f"💰 GOLD: {p:.2f}$ RSI: {int(rsi)}")
            elif txt=="/status": send(cid,f"✅ V14 AUTO LIVE\n🔔 Авто каждые 35 мин\n👥 Подписчиков: {len(CHATS)}\n🟢 Работает 24/7")
            elif txt=="/stop":
                CHATS.discard(cid)
                send(cid,"🔕 Авто выкл. /start чтобы вкл снова")
    except: time.sleep(3)
