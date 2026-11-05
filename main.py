# -*- coding: utf-8 -*-
import threading, os, requests, time
from flask import Flask
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "V16 AUTO TRADER LIVE"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
CHATS = set()
BALANCE = 1000.0
POSITION = None # {"type": "BUY", "entry": price}
TRADES = []

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

def trader_loop():
    global BALANCE, POSITION
    last_sig = ""
    while True:
        time.sleep(300) # каждые 5 мин
        if not CHATS: continue
        p,rsi,sig,pw=get_gold()
        if not p: continue
        if sig not in ["ПОКУПКА","ПРОДАЖА"]: continue
        if sig==last_sig: continue
        last_sig=sig
        
        # АВТО-ТРЕЙДИНГ
        profit_text=""
        if POSITION is None:
            # Открываем сделку
            POSITION={"type":sig,"entry":p,"rsi":rsi,"power":pw}
            profit_text=f"💼 ОТКРЫЛ СДЕЛКУ: {sig} по {p:.2f}"
        else:
            # Закрываем противоположную и открываем новую
            entry=POSITION["entry"]
            if POSITION["type"]=="ПОКУПКА":
                profit = p - entry
                pct = profit/entry*100
            else:
                profit = entry - p
                pct = profit/entry*100
            
            BALANCE += profit
            TRADES.append(profit)
            win = "✅" if profit>0 else "❌"
            profit_text=f"{win} ЗАКРЫЛ {POSITION['type']} {entry:.2f}->{p:.2f} Профит: {profit:+.2f}$ ({pct:+.2f}%)\n💰 Баланс: {BALANCE:.2f}$"
            POSITION={"type":sig,"entry":p,"rsi":rsi,"power":pw}
            profit_text+=f"\n💼 ОТКРЫЛ НОВУЮ: {sig} по {p:.2f}"

        if sig=="ПОКУПКА":
            txt=f"🚨 СИГНАЛ BUY + АВТО-ТРЕЙД!\n\n🟢 ПОКУПКА\n🔥 Сила: {pw}%\n📈 RSI: {int(rsi)}\n💰 Цена: {p:.2f}$\n\n{profit_text}"
        else:
            txt=f"🚨 СИГНАЛ SELL + АВТО-ТРЕЙД!\n\n🔴 ПРОДАЖА\n🔥 Сила: {pw}%\n📉 RSI: {int(rsi)}\n💰 Цена: {p:.2f}$\n\n{profit_text}"

        for cid in list(CHATS):
            send(cid,txt)

threading.Thread(target=trader_loop, daemon=True).start()
print("V16 TRADER STARTED")
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
                send(cid,"✨ V16 AUTO TRADER MAX ✨\n🤖 Сам торгует виртуально!\n💰 Старт: 1000$\n🧠 Шлет только BUY/SELL\n\n📊 /check - сигнал\n💰 /balance - баланс\n📈 /trades - сделки\n⚙️ /status - статус")
            elif txt=="/check":
                p,rsi,sig,pw=get_gold()
                if not p: send(cid,"⏳ Думаю...")
                elif sig=="ПОКУПКА": send(cid,f"🟢 ПОКУПКА {pw}% RSI {int(rsi)} {p:.2f}")
                elif sig=="ПРОДАЖА": send(cid,f"🔴 ПРОДАЖА {pw}% RSI {int(rsi)} {p:.2f}")
                else: send(cid,f"⏳ БОКОВИК {pw}% RSI {int(rsi)} {p:.2f}")
            elif txt=="/balance":
                pos = f"\n💼 Позиция: {POSITION['type']} с {POSITION['entry']:.2f}" if POSITION else "\n💼 Позиций нет"
                wins = sum(1 for t in TRADES if t>0)
                send(cid,f"💰 БАЛАНС АВТО-ТРЕЙДЕРА\n💵 {BALANCE:.2f}$ (старт 1000$)\n📊 Сделок: {len(TRADES)} Побед: {wins}{pos}")
            elif txt=="/trades":
                if not TRADES: send(cid,"📈 Сделок пока нет, ждем сигнал BUY/SELL")
                else:
                    total=sum(TRADES)
                    send(cid,f"📈 СДЕЛКИ: {len(TRADES)}\n💰 Общий профит: {total:+.2f}$\n💵 Баланс: {BALANCE:.2f}$")
            elif txt=="/status": send(cid,f"✅ V16 TRADER LIVE\n💰 Баланс: {BALANCE:.2f}$\n👥 Подписчиков: {len(CHATS)}\n🤖 Авто-трейдинг ON")
    except: time.sleep(3)
