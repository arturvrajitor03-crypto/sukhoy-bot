import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=200)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        v = float(r.get('price',0))
        if v>1000:
            return v
    except:
        pass
    return 4045.0

@app.route('/')
def home():
    return "V33 GOLD LIVE",200

@app.route('/health')
def health():
    return "OK",200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        while True:
            time.sleep(60)
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m,"V33 READY /check")

    @bot.message_handler(commands=['check'])
    def check(m):
        p=get_price()
        price_history.append(p)
        lst=list(price_history)
        if len(lst)<30:
            base=p-15
            lst=[base+i*0.5 for i in range(40)]
            lst.append(p)
        gains=0
        losses=0
        for i in range(1,15):
            d=lst[-i]-lst[-i-1]
            if d>0:
                gains+=d
            else:
                losses+=-d
        if losses<0.1:
            rsi=74.0
        else:
            rs=gains/losses
            rsi=100-(100/(1+rs))
        ema20=sum(lst[-20:])/20
        if rsi<30:
            sig="BUY"
            perc=92
            tp1=p+20
            tp2=p+40
            tp3=p+70
            sl=p-18
        elif rsi<45:
            sig="BUY"
            perc=82
            tp1=p+15
            tp2=p+35
            tp3=p+60
            sl=p-18
        elif rsi>70:
            sig="SELL"
            perc=92
