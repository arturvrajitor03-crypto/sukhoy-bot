import os, threading, requests
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

@app.route('/')
def home():
    return "V30 MULTI TP Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V30 STARTED")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "V30 READY /check")

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
       
