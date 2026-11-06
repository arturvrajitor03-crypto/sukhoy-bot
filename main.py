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
from datetime import datetime
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
    return 4045.80

@app.route('/')
def home():
    return "V36 BEST GOLD %s LIVE" % get_price(),200

@app.route('/health')
def health():
    return "OK",200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN WEB LIVE")
        while True:
            time.sleep(60)
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)

    POK=D("0J/QntCa0KPQn9Ca0JA=")
    PRO=D("0J/RgNCe0JTQkNCW0JA=")
    BOK=D("0JHQntCa0J7QktCY0Kg=")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m,"GOLD PRO V36 BEST\n/check - signal\n/status - check")

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
        losses=
