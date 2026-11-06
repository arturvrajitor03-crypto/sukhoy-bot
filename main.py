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
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        v = float(r.get('price', 0))
        if v > 1000:
            return v
    except:
        pass
    return 4045.0

@app.route('/')
def home():
    return "V31 MULTI TP GOLD {} LIVE".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("BOT THREAD START")
    if not BOT_TOKEN or len(BOT_TOKEN) < 10:
        print("NO TOKEN - BOT DISABLED BUT WEB STILL LIVE")
        while True:
            time.sleep(60)
    try:
        import telebot
        bot = telebot.TeleBot(BOT_TOKEN)
        print("TELEBOT OK")

        @bot.message_handler(commands
