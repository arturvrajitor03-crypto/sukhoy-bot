import os, time, threading, requests, math
from flask import Flask
import telebot

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
CHAT_ID = None
SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT"]
positions = {}
balance = 500.0

@app.route('/')
def home():
    return "Mashinka ON"

def klines(s):
    try:
        u = "https://testnet.binance.vision/api/v3/klines"
        p = {"symbol": s, "interval": "15m", "limit": 100}
        r = requests.get(u, params=p, timeout=10).json()
        return [float(x[4]) for x in r]
    except:
        return []

def rsi(c):
    if len(c) < 15: return 50
    g=[]; l=[]
    for i in range(1,len(c)):
        d=c[i]-c[i-1]
        g.append(max(d,0)); l.append(max(-d,0))
    ag=sum(g[-14:])/14; al=sum(l[-14:])/14
    if al==0: return 100
    return 100-(100/(1+ag/al))

def ema(c, n):
    k=2/(n+1); e=c[0]
    for p in c[1:]: e=p*k+e*(1-k)
    return e

def price(s):
    try:
        u="https://testnet.binance.vision/api/v3/ticker/price"
        r=requests.get(u, params={"symbol":s}, timeout=10).json()
        return float(r['price'])
    except: return None

def send(t):
    global CHAT_ID
    if CHAT_ID:
        try: bot.send_message(CHAT_ID,t)
        except: pass
    print(t)

def loop():
    global balance
    time.sleep(10)
    send("Mashinka zapushena! Depozit 500$ Sdelka 50$")
    while True:
        try:
            for s in SYMBOLS:
                c=klines(s)
                if not c: continue
                p=c[-1]; r=rsi(c); e20=ema(c,20); e50=ema(c,50)
                if s in positions:
                    en=positions[s]["price"]
                    pnl=(p-en)/en*100
                    if pnl>=4:
                        del positions[s]
                        balance+=50*pnl/100
                        send("PRODAZHA "+s+" +"+str(round(pnl,2))+"%")
                    elif pnl<=-2.5:
                        del positions[s]
                        balance+=50*pnl/100
                        send("STOP "+s+" "+str(round(pnl,2))+"%")
                    continue
                # 3 indikatora: RSI + EMA20 + EMA50
                score=0
                if r<45: score+=1
                if p>e20: score+=1
                if e20>e50: score+=1
                if score>=2:
                    q=math.floor((50/p)*100000)/100000
                    positions[s]={"price":p,"qty":q}
                    send("POKUPKA "+s+" "+str(round(p,2))+" RSI "+str(round(r,1))+" Skor "+str(score)+"/3")
            time.sleep(60)
        except Exception as e:
            print(e); time.sleep(60)

@bot.message_handler(commands=['start'])
def st(m):
    global CHAT_ID; CHAT_ID=m.chat.id
    bot.reply_to(m,"Mashinka rabotaet! /status /signal /balance")

@bot.message_handler(commands=['status'])
def st2(m):
    if not positions:
        bot.reply_to(m,"Net pozicij. Zhdem..."); return
    t="Pozicii:\n"
    for s,v in positions.items():
        cur=price(s); pnl=(cur-v["price"])/v["price"]*100
        t+=s+": "+str(round(pnl,2))+"%\n"
    bot.reply_to(m,t)

@bot.message_handler(commands=['signal'])
def sg(m):
    t="Signaly:\n"
    for s in SYMBOLS:
        c=klines(s)
        if not c: continue
        p=c[-1]; r=rsi(c); e20=ema(c,20); e50=ema(c,50)
        t+=s+" "+str(round(p,2))+" RSI "+str(round(r,1))+" EMA20 "+str(round(e20,2))+"\n"
    bot.reply_to(m,t)

@bot.message_handler(commands=['balance'])
def bl(m):
    bot.reply_to(m,"Balans: "+str(round(balance,2))+"$ Pozicij: "+str(len(positions)))

threading.Thread(target=loop, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
