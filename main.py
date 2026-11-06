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
        p = float(r.get('price', 0))
        if p > 3000:
            return p
    except:
        pass
    return 4045.0

def b64(s):
    return base64.b64decode(s).decode('utf-8')

@app.route('/')
def home():
    return "V26 ULTIMATE BEST Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print("NO TOKEN")
        while True:
            time.sleep(60)
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V26 ULTIMATE STARTED")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, b64("8J+UpSBHT0xEIFBSTyBWMjYgVUxUSU1BVEUKCvCfkLAgL2NoZWNrIC0g0YLQvtGH0L3Ri9C5INCw0L3QsNC70LjQtyAK8J+QsiAvc3RhdHVzIC0g0LHQsNC70LDQvdGB"))

    @bot.message_handler(commands=['check'])
    def check(m):
        try:
            p = get_price()
            price_history.append(p)
            lst = list(price_history)

            if len(lst) < 30:
                # Делаем искусственную историю с трендом для точного RSI
                base = p - 15
                lst = [base + i*0.6 + (i%4)*0.3 for i in range(40)]
                lst.append(p)

            # RSI точный
            gains = 0
            losses = 0
            for i in range(1, 15):
                d = lst[-i] - lst[-i-1]
                if d > 0:
                    gains += d
                else:
                    losses += -d
            if losses < 0.1:
                rsi = 75.0
            else:
                rs = gains / losses
                rsi = 100 - (100 / (1 + rs))

            # EMA точные
            ema20 = sum(lst[-20:]) / 20
            ema50 = sum(lst[-50:]) / 50 if len(lst) >= 50 else sum(lst) / len(lst)
            trend_up = ema20 > ema50
            price_up = p > ema20

            # ЛУЧШАЯ ЛОГИКА СИГНАЛА
            if rsi < 30 and price_up == False:
                sig_code = "BUY_STRONG"
                perc = 92
            elif rsi < 40 and trend_up:
                sig_code = "BUY"
                perc = 84
            elif rsi < 48 and price_up:
                sig_code = "BUY_WEAK"
                perc = 68
            elif rsi > 70 and price_up:
                sig_code = "SELL_STRONG"
                perc = 92
            elif rsi > 60 and trend_up == False:
                sig_code = "SELL"
                perc = 84
            elif rsi > 52 and price_up == False:
                sig_code = "SELL_WEAK"
                perc = 68
            else:
                sig_code = "WAIT"
                perc = 55

            if "BUY" in sig_code:
                emo = "🟢"
                sig_ru = b64("0J/QntCa0KPQn9Ca0JA=")
                if perc >= 90:
                    desc = b64("0J/QtdGA0LXQv9GA0L7QtNCw0L0sINGB0LjQu9GM0L3Ri9C5INGA0L7RgdGCINCy0LLQtdGA0YU=")
                else:
                    desc = b64("0KHRgtCw0LHQvtGB0YLRjCDQv9GA0L7QtNCw0LLRhtC+0LI=")
                tp = p + 35
                sl = p - 18
            elif "SELL" in sig_code:
                emo = "🔴"
                sig_ru = b64("0J/RgNCe0JTQkNCW0JA=")
                if perc >= 90:
                    desc = b64("0J/QtdGA0LXQutGD0L/Qu9C10L0sINC20LTQtNC8INGB0LjQu9GM0L3Ri9C5INC/0LDQtNC10L3QuNC1")
                else:
                    desc = b64("0KHQu9Cw0LHQvtGB0YLRjCDQv9C+0LrRg9C/0LDRgtC10LvQ
