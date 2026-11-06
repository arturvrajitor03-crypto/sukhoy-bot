import os, time, threading, requests, base64
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=200)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4045))
    except:
        return 4045.0

def D(s):
    return base64.b64decode(s).decode('utf-8')

@app.route('/')
def home():
    return "V29 MULTI TP RUS Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V29 STARTED")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "V29 MULTI TP READY /check")

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        lst = list(price_history)
        if len(lst) < 30:
            base = p - 15
            lst = [base + i*0.6 for i in range(40)]
            lst.append(p)

        gains = 0
        losses = 0
        for i in range(1, 15):
            d = lst[-i] - lst[-i-1]
            if d > 0:
                gains += d
            else:
                losses += -d
        if losses < 0.1:
            rsi = 74.0
        else:
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs))

        ema20 = sum(lst[-20:]) / 20
        ema50 = sum(lst[-50:]) / 50 if len(lst) >= 50 else ema20

        POK = D("0J/QntCa0KPQn9Ca0JA=")
        PRO = D("0J/RgNCe0JTQkNCW0JA=")
        BOK = D("0JHQntCa0J7QktCY0Kg=")
        ZOL = D("0JfQntCb0J7QotCe")
        VHO = D("0JLRhdC+0LQ=")
        STO = D("0KHRgtC+0L8=")
        VRE = D("0JLRgNC10LzRjw==")
        TP1 = D("0KLQnDE=")
        TP2 = D("0KLQnDI=")
        TP3 = D("0KLQnDM=")

        if rsi < 30:
            sig = POK
            perc = 92
            emo = "🟢"
            tp1 = p + 20
            tp2 = p + 40
            tp3 = p + 70
            sl = p - 18
        elif rsi < 45:
            sig = POK
            perc = 82
            emo = "🟢"
            tp1 = p + 15
            tp2 = p + 35
            tp3 = p + 60
            sl = p - 18
        elif rsi > 70:
            sig = PRO
            perc = 92
            emo = "🔴"
            tp1 = p - 20
            tp2 = p - 40
            tp3 = p - 70
            sl = p + 18
        elif rsi > 55:
            sig = PRO
            perc =
