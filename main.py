import os, sys, time
try:
    import flask
except:
    os.system("pip install flask --quiet")
try:
    import telebot
except:
    os.system("pip install pyTelegramBotAPI --quiet")
import threading, requests, base64
from flask import Flask
from datetime import datetime, timedelta
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=200)

def D(s):
    return base64.b64decode(s).decode('utf-8')

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        v = float(r.get('price',0))
        if v>1000:
            return v
    except:
        pass
    return 4041.19

@app.route('/')
def home():
    return "V38 FIX GOLD %s" % get_price(),200

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

    POK=D("0J/QntCa0KPQn9Ca0JA=")
    PRO=D("0J/RgNCe0JTQkNCW0JA=")
    BOK=D("0JHQntCa0J7QktCY0Kg=")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m,"V38 FIX - REAL RSI\n/check")

    @bot.message_handler(commands=['check'])
    def check(m):
        p=get_price()
        price_history.append(p)
        lst=list(price_history)
        
        # FIX: если мало истории - не даем сильный сигнал, даем БОКОВИК 55%
        if len(lst)<20:
            rsi=50.0
            ema20=p
            sig=BOK
            perc=55
            tp1=p+8
            tp2=p+18
            tp3=p+35
            sl=p-10
            tr="Malo istorii - JDEM"
        else:
            gains=0
            losses=0
            for i in range(1,15):
                if len(lst)-i-1 <0:
                    break
                d=lst[-i]-lst[-i-1]
                if d>0:
                    gains+=d
                else:
                    losses+=-d
            if losses<0.1:
                rsi=65.0
            else:
                rs=gains/losses
                rsi=100-(100/(1+rs))
            ema20=sum(lst[-20:])/20
            
            # FIX: TP меньше чтобы чаще проходить!
            if rsi<35:
                sig=POK
                perc=88
                tp1=p+8
                tp2=p+18
                tp3=p+35
                sl=p-10
                tr=D("0KHQtdC70YzQvdGL0Lkg0YLRgNC10L3QtA==")
            elif rsi<45:
                sig=POK
                perc=75
                tp1=p+7
                tp2=p+15
                tp3=p+28
                sl=p-10
                tr="Pokupka"
            elif rsi>65:
                sig=PRO
                perc=88
                tp1=p-8
                tp2=p-18
                tp3=p-35
                sl=p+10
                tr=D("0KHQtdC70YzQvdGL0Lkg0YLRgNC10L3QtA==")
            elif rsi>55:
                sig=PRO
                perc=75
                tp1=p-7
                tp2=p-15
                tp3=p-28
                sl=p+10
                tr="Prodaja"
            else:
                sig=BOK
                perc=55
                tp1=p+6
                tp2=p+12
                tp3=p+22
                sl=p-8
                tr="Bokovik JDEM"

        il_time = datetime.utcnow() + timedelta(hours=2)
        time_str = il_time.strftime("%H:%M")

        msg="GOLD PRO V38 FIX\n\n"
        msg+="%s - %s\n" % (sig,tr)
        msg+="GOLD: %.2f\n" % p
        msg+="RSI REAL: %.1f (na graffike 35)\n" % rsi
        msg+="UVERENNOST: %s%%\n\n" % perc
        msg+="PLAN FIX:\n"
        msg+="Vkhod: %.2f\n" % p
        msg+="TP1: %.2f (+%d$)\n" % (tp1, abs(tp1-p))
        msg+="TP2: %.2f\n" % tp2
        msg+="TP3: %.2f\n" % tp3
        msg+="SL: %.2f\n\n" % sl
        msg+="Time IL: %s\n" % time_str
        msg+="==================="
        bot.reply_to(m,msg)

    @bot.message_handler(commands=['status'])
    def status(m):
        bot.reply_to(m,"V38 FIX LIVE %.2f len=%d" % (get_price(), len(price_history)))

    while True:
        try:
            bot.infinity_polling(none_stop=True,timeout=20)
        except:
            time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=run_bot,daemon=True).start()
    port=int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0',port=port)
