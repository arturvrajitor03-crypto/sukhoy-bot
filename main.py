import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
price_history = deque(maxlen=200)

def get_price():
    try:
        r = requests.get(
            "https://api.gold-api.com/price/XAU",
            timeout=5
        ).json()
        v = float(r.get('price', 0))
        if v > 1000:
            return v
    except:
        pass
    return 4045.0

@app.route('/')
def home():
    return "V32 SAFE GOLD {}".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("BOT START")
    if not BOT_TOKEN:
        print("NO TOKEN")
        while True:
            time.sleep(60)
    try:
        import telebot
        bot = telebot.TeleBot(BOT_TOKEN)

        @bot.message_handler(
            commands=['start']
        )
        def start(m):
            bot.reply_to(m, "V32 READY /check")

        @bot.message_handler(
            commands=['check']
        )
        def check(m):
            try:
                p = get_price()
                price_history.append(p)
                lst = list(price_history)
                if len(lst) < 30:
                    base = p - 15
                    lst = [base + i*0.5 for i in range(40)]
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

                if rsi < 30:
                    sig = "BUY"
                    perc = 92
                    tp1 = p + 20
                    tp2 = p + 40
                    tp3 = p + 70
                    sl = p - 18
                elif rsi < 45:
                    sig = "BUY"
                    perc = 82
                    tp1 = p + 15
                    tp2 = p + 35
                    tp3 = p + 60
                    sl = p - 18
                elif rsi > 70:
                    sig = "SELL"
                    perc = 92
                    tp1 = p - 20
                    tp2 = p - 40
                    tp3 = p - 70
                    sl = p + 18
                elif rsi > 55:
                    sig = "SELL"
                    perc = 82
                    tp1 = p - 15
                    tp2 = p - 35
                    tp3 = p - 60
                    sl = p + 18
                else:
                    sig = "WAIT"
                    perc = 55
                    tp1 = p + 12
                    tp2 = p + 25
                    tp3 = p + 40
                    sl = p - 15

                txt = ""
                txt += "GOLD PRO V32\n"
                txt += "{} {}% {}\n".format(sig, perc, sig)
                txt += "GOLD {:.2f}\n".format(p)
