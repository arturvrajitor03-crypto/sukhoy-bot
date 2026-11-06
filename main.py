import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")

BALANCE = 1000.0
price_history = deque(maxlen=100)
open_trades = []

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        p = float(r.get('price', 0))
        if p > 3000:
            return p
    except:
        pass
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT", timeout=5).json()
        return float(r['result']['list'][0]['lastPrice'])
    except:
        pass
    return 4042.8

def calc_rsi(prices):
    if len(prices) < 15:
        return 50.0
    gains = 0
    losses = 0
    for i in range(1, 15):
        diff = prices[-i] - prices[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses += -diff
    if losses == 0:
        return 80.0
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def calc_ema(prices, period):
    if len(prices) < period:
        return prices[-1]
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

@app.route('/')
def home():
    price = get_gold_price()
    return "V19 STABLE Gold {} TOKEN OK".format(price), 200

@app.route('/health')
def health():
    return "OK", 200

def run_telegram():
    if not BOT_TOKEN:
        print("NO TOKEN")
        time.sleep(60)
        return
    
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V19 STABLE started!")

    @bot.message_handler(commands=['start'])
    def start_msg(m):
        text = (
            "GOLD BOT V19 STABLE\n\n"
            "Commands:\n"
            "/check - price\n"
            "/status - balance\n"
            "/trades - deals"
        )
        bot.reply_to(m, text)

    @bot.message_handler(commands=['check'])
    def check_msg(m):
        price = get_gold_price()
        price_history.append(price)
        
        prices = list(price_history)
        if len(prices) < 20:
            prices = [4040 + i * 0.3 for i in range(50)]
        
        rsi = calc_rsi(prices)
        ema20 = calc_ema(prices, 20)
        ema50 = calc_ema(prices, 50)
        
        if rsi < 35:
            sig = "BUY"
            perc = 88
        elif rsi > 65:
            sig = "SELL"
            perc = 88
        else:
            sig = "WAIT"
            perc = 60
        
        if sig == "BUY":
            icon = "BUY"
            tp = price + 30
            sl = price - 20
        elif sig == "SELL":
            icon = "SELL"
            tp = price - 30
            sl = price + 20
        else:
            icon = "WAIT"
            tp = price
            sl = price

        txt = (
            "GOLD PRO V19\n\n"
            "Signal: {} {}\n"
            "Price: {:.2f} $\n\n"
            "RSI: {:.1f}\n"
            "EMA20: {:.2f}\n"
            "EMA50: {:.2f}\n"
            "Conf: {}%\n\n"
            "Plan:\n"
            "Entry: {:.2f}\n"
            "TP: {:.2f}\n"
            "SL: {:.2f}\n\n"
            "Time: {}\n"
            "Balance: {:.2f} $"
        ).format(icon, sig
