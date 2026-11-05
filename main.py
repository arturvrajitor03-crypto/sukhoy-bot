import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home(): return "SUHOY CLEAN BOT"

def get_price():
    try: return float(requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()['price'])
    except: return 4120.8

def make_image(entry, sl, tp1, tp2, tp3):
    # Пробуем твой золотой шаблон
    try:
        base = Image.open("template.jpg").convert("RGB")
        W, H = base.size
        base = base.resize((W*3, H*3))  # Увеличиваем в 3 раза!
        W, H = base.size
    except:
        W, H = 1200, 1200
        base = Image.new('RGB', (W, H), (10,10,10))
        draw = ImageDraw.Draw(base)
        draw.rectangle([0,0,W,H], outline=(255,215,0), width=20)
        base = base
    draw = ImageDraw.Draw(base)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(W*0.09))
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(W*0.05))
        f3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(W*0.03))
    except:
        f1 = f2 = f3 = ImageFont.load_default()

    # Чистим центр черным чтобы цифры были видны
    draw.rectangle([W*0.05, H*0.35, W
