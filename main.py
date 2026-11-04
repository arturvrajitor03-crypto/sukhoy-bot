import asyncio
import random
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---- Цена золота ----
def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get("price", 4065))
    except:
        return random.uniform(4055, 4075)

# ---- Картинка СУХОЙ ----
def create_card(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (600, 850), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # Рамка золотая
    draw.rectangle([5,5,595,845], outline=(212,175,55), width=4)
    draw.rectangle([15,15,585,835], outline=(212,175,55), width=1)

    # Текст
    try:
        font_big = ImageFont.truetype("arial.ttf", 38)
        font_mid = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except:
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((150, 30), "👑 СУХОЙ - XAUUSD", fill=(212,175,55), font=font_big)
    draw.text((160, 90), f"XAUUSD - {direction}", fill=(255,0,0) if direction=="SELL" else (0,255,0), font=font_mid)
    
    # Бык по центру (эмодзи заменит текст если нет картинки)
    draw.text((210, 180), "🐂", fill=(212,175,55), font=ImageFont.truetype("arial.ttf", 120) if os.path.exists("arial.ttf") else font_big)

    draw.text((150, 420), f"Вход: ниже {entry}", fill="white", font=font_mid)
    draw.text((200, 460), f"SL: {sl}", fill="white", font=font_mid)
    draw.text((180, 500), f"TP1: {tp1} ⬜", fill="white", font=font_mid)
    draw.text((180, 535), f"TP2: {tp2} ⬜", fill="
