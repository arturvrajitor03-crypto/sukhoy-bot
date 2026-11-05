import os
import requests
import threading
import random
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")

fapp = Flask(__name__)

@fapp.route('/')
def home():
    return "BOT ALIVE - 4065 FIXED"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get("price", 4065))
        return int(price)
    except:
        return 4065

def make_card(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (600, 850), (15, 15, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 595, 845], outline=(212, 175, 55), width=4)
    font = ImageFont.load_default()
    color = (255, 70, 70) if direction == "SELL" else (70, 255, 70)
    draw.text((110, 30), "SUHOY - XAUUSD", fill=(212, 175, 55), font=font)
    draw.text((150, 80), f"{direction} {entry}$", fill=color, font=font)
    draw.text((260, 200), "BULL", fill=(212, 175, 55), font=font)
    draw.text((150, 400), f"Entry below {entry}",
