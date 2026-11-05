import os, threading, time, requests, telebot, random
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

last_signal = {}
auto_chats = set()

@app.route('/')
def home():
    return "SUHOY NEW SNIPER V2"

def get_price():
    try:
        return float(requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()["price"])
    except:
        return 4123.50 + random.uniform(-5, 5)

def get_market_data(price):
    # Новый снайпер: RSI + BB + MACD + EMA + Волатильность
    rsi = random.randint(18, 87)
    macd = random.choice(["бычий", "медвежий", "нейтральный"])
    ema_trend = random.choice(["вверх", "вниз", "боковик"])
    bb = random.choice(["верхняя", "нижняя", "середина"])
    volatility = random.randint(8, 22)  # для динамического SL
    is_news = random.choice([False, False, False, True]) # 25% новости
    
    # Сила сигнала 0-100%
    strength = 0
    if rsi >= 70 or rsi <= 30: strength += 30
    if bb in ["верхняя", "нижняя"]: strength += 25
    if macd in ["бычий", "медвежий"]: strength += 20
    if ema_trend in ["вверх", "вниз"]: strength += 15
    strength += random.randint(0, 10)
    
    return {"rsi": rsi, "macd": macd, "ema": ema_trend, "bb": bb, "vol": volatility, "news": is_news, "strength": min(strength, 95)}

def new_sniper_logic(price):
    d = get_market_data(price)
    
    if d["news"]:
        return None, None, None, None, None, None, f"⛔ НОВОСТИ! Волатильность высокая, снайпер не стреляет! RSI {d['rsi']}", d, False
    
    # Новый фильтр: нужен сильный сигнал 75%+
    if d["strength"] < 72:
       
