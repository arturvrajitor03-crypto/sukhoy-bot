import os
import random
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Flask чтобы Render не падал ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "👑 SUHOY BOT IS ALIVE"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# --- Цена золота ---
def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get("price", 4065))
    except:
        return 4065.0

# --- Картинка ---
def create_card(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (600, 850), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5,5,595,845], outline=(212,175,55), width=4)
    
    try:
       
