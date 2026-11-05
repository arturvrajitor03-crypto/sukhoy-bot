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
    return "SUHOY NEW SNIPER V2 FIXED"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4123.50

def get_market_data(price):
    rsi = random.randint(18, 87)
    macd = random.choice(["бычий", "медвежий"])
    bb = random.choice(["верхняя", "нижняя", "середина"])
    vol = random.randint(8, 22)
    strength = random.randint(60, 95)
    is_news = random.choice([False, False, False, True])
    return {"rsi": rsi, "macd": macd, "bb": bb, "vol": vol, "strength": strength, "news": is_news}

def new_sniper_logic(price):
    d = get_market_data(price)
    if d["news"]:
        return None, None, None, None, None, None, "⛔ НОВОСТИ! Снайпер ждет
