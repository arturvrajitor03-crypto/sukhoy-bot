import os, threading, time, requests, telebot, random
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

last_signal = {}
auto_chats = set()

@app.route('/')
def home():
    return "SUHOY SNIPER FIXED NO EMOJI"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4123.50

def get_market_data(price):
    rsi = random.randint(18, 87)
    macd = random.choice(["bull", "bear"])
    bb = random.choice(["upper", "lower", "middle"])
    vol = random.randint(8, 22)
    strength = random.randint(60, 95)
    is_news = random.choice([False, False, False, True])
    return {"rsi": rsi, "macd": macd, "bb": bb, "vol": vol, "strength": strength, "news": is_news}

def new_sniper_logic(price):
    d = get_market_data(price)
    if d["news"]:
        return None, None, None, None, None, None, "NEWS! Sniper wait", d, False
    if d["strength"] < 72:
        msg = f"WAIT Strength {d['strength']}% RSI {d['rsi']} weak"
        return None, None, None, None, None, None, msg, d, False
    if d["rsi"] >= 70 and d["bb"] == "upper":
        sl = price + d["vol"]
        tp1 = price - 9
        tp2 = price - 20
        tp3 = price - 35
        reason = f"SELL Strength {d['strength']}% RSI {d['rsi']} BB {d['bb']}"
        return "SELL", price, sl, tp1, tp2, tp3, reason, d, True
    if d["rsi"] <= 30 and d["bb"] == "lower":
        sl = price - d["vol"]
        tp1 = price + 
