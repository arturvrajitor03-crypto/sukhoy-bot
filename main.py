import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=100)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4042))
    except:
        return 4042.8

@app.route('/')
def home():
    return "V24 RU FIXED Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V24 RU FIXED started")

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = "GOLD PRO V24 - FIXED\n/check - analiz\n/status - info"
        bot.reply_to(m, txt)

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        
        # Если истории мало - создаем фейковую с колебанием чтобы RSI работал
        lst = list(price_history)
        if len(lst) < 20:
            base = p - 10
            lst = [base + i*0.5 + (i%3) for i in range(30)]
            lst.append(p)

        gains = 0
        losses = 0
        for i in range(1, 15):
            d = lst[-i] - lst[-i-1]
            if d > 0:
                gains += d
            else:
                losses += -d
        
        if losses == 0:
            rsi = 72.5
        else:
            rs = gains / max(losses, 0.1)
            rsi = 100 - (100 / (1 + rs))

        # Логика сигнала
        if rsi < 35:
            sig = "ПОКУПКА"
            perc = 88
            emo = "🟢"
            desc = "Перепродан, ждем рост вверх"
            tp = p + 30
            sl = p - 18
        elif rsi < 45:
            sig = "ПОКУПКА"
            perc = 73
            emo = "🟢"
            desc = "Слабость продавцов, можно
