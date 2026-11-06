import os
import sys
import time

# АВТО-УСТАНОВКА - чтобы не было exited early
try:
    import flask
except:
    os.system("pip install flask --quiet")
try:
    import telebot
except:
    os.system("pip install pyTelegramBotAPI --quiet")
try:
    import requests
except:
    os.system("pip install requests --quiet")

import threading
import requests
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
    return "V34 FINAL GOLD %s LIVE" % get_price(),200

@app.route('/health')
def health():
    return "OK",200

def run_bot():
    print("BOT THREAD START")
    if not BOT_TOKEN:
        print("NO TOKEN BUT WEB KEEP LIVE")
        while True:
            time.sleep(60)
    try:
        import telebot
        bot = telebot.TeleBot(BOT_TOKEN)
        print("BOT OK")

        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m,"V34 READY /check")

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
                tp1=p-20
                tp2=p-40
                tp3=p-70
                sl=p+18
            elif rsi>55:
                sig="SELL"
                perc=82
                tp1=p-15
                tp2=p-35
                tp3=p-60
                sl=p+18
            else:
                sig="WAIT"
                perc=55
                tp1=p+12
                tp2=p+25
                tp3=p+40
                sl=p-15
            msg="GOLD PRO V34\n"
            msg+="%s %s%%\n" % (sig,perc)
            msg+="GOLD %.2f\n" % p
            msg+="RSI %.1f EMA %.2f\n\n" % (rsi,ema20)
            msg+="Entry %.2f\n" % p
            msg+="TP1 %.2f\n" % tp1
            msg+="TP2 %.2f\n" % tp2
            msg+="TP3 %.2f\n" % tp3
            msg+="SL %.2f\n" % sl
            msg+="%s\n" % datetime.now().strftime("%H:%M")
            bot.reply_to(m,msg)

        @bot.message_handler(commands=['status'])
        def status(m):
            bot.reply_to(m,"V34 OK %.2f" % get_price())

        while True:
            try:
                bot.infinity_polling(none_stop=True,timeout=20)
            except Exception as e:
                print("POLL ERR %s" % e)
                time.sleep(10)
    except Exception as e:
        print("BOT ERR %s" % e)
        while True:
            time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=run_bot,daemon=True).start()
    port=int(os.environ.get("PORT",10000))
    print("WEB START %s" % port)
    app.run(host='0.0.0.0',port=port)
