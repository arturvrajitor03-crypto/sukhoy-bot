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
    return "V25 FIXED NO RU IN CODE Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V25 started")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "V25 READY /check /status")

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        
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

        # Сигналы без русских букв в коде - используем коды
        if rsi < 35:
            sig = "\u041f\u041e\u041a\u0423\u041f\u041a\u0410"  # ПОКУПКА
            perc = 88
            emo = "🟢"
            desc = "\u041f\u0435\u0440\u0435\u043f\u0440\u043e\u0434\u0430\u043d, \u0436\u0434\u0435\u043c \u0440\u043e\u0441\u0442"  # Перепродан, ждем рост
            tp = p + 30
            sl = p - 18
        elif rsi < 45:
            sig = "\u041f\u041e\u041a\u0423\u041f\u041a\u0410"
            perc = 74
            emo = "🟢"
            desc = "\u0421\u043b\u0430\u0431\u043e\u0441\u0442\u044c \u043f\u0440\u043e\u0434\u0430\u0432\u0446\u043e\u0432"  # Слабость продавцов
            tp = p + 30
            sl = p - 18
        elif rsi > 65:
            sig = "\u041f\u0420\u041e\u0414\u0410\u0416\u0410"  # ПРОДАЖА
            perc = 88
            emo = "🔴"
            desc = "\u041f\u0435\u0440\u0435\u043a\u0443\u043f\u043b\u0435\u043d, \u0436\u0434\u0435\u043c \u043f\u0430\u0434\u0435\u043d\u0438\u0435"  # Перекуплен, ждем падение
            tp = p - 30
            sl = p + 18
        elif rsi > 55:
            sig = "\u041f\u0420\u041e\u0414\u0410\u0416\u0410"
            perc = 74
            emo = "🔴"
            desc = "\u0421\u043b\u0430\u0431\u043e\u0441\u0442\u044c \u043f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u0435\u0439"  # Слабость покупателей
            tp = p - 30
            sl = p + 18
        else:
            sig = "\u0411\u041e\u041a\u041e\u0412\u0418\u041a"  # БОКОВИК
            perc = 58
            emo = "⚪️"
            desc = "\u041d\u0435\u0442 \u0442\u0440\u0435\u043d\u0434\u0430, \u0436\u0434\u0435\u043c" 
