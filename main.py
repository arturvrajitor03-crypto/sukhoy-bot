import os, requests, random, threading, time
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)
active_trades = {}

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get("price", 0))
        if price > 1000:
            return int(price)
    except:
        pass
    return 4077

def analyze_market(price):
    if price >= 4050:
        direction = "BUY"
        entry = f"выше {price}"
        sl = price - 9
        tp1 = price + 4
        tp2 = price + 8
        tp3 = price + 13
    else:
        direction = "SELL"
        entry = f"ниже {price}"
        sl = price + 9
        tp1 = price - 4
        tp2 = price - 8
        tp3 = price - 13
    return direction, entry, sl, tp1, tp2, tp3, price

def find_template():
    for f in os.listdir("."):
        if f.lower().endswith((".jpg",".jpeg",".png",".webp")):
            if "main" not in f.lower():
                return f
    return None

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def create_signal_image(template_path, direction, entry, sl, tp1, tp2, tp3, hit_tps):
    base = Image.open(template_path).
