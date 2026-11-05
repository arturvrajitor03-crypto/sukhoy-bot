import os, io, requests, random
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return round(float(r.get('price', 4128)), 2)
    except:
        return round(4128.70 + random.uniform(-2,2), 2)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arial.ttf"
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

def make_signal(price, direction):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    
    font_1 = get_font(60, False)
    font_2 = get_font(110, True)
    font_3 = get_font(58, True)
    
    if direction == "BUY":
        color = (0, 255, 100)
        sl = round(price - 8.5, 2)
        tp1 = round(price + 8, 2)
        tp2 = round(price + 16, 2)
        tp3 = round(price + 28, 2)
    else:
        color = (255, 80, 80)
        sl = round(price + 8.5, 2)
        tp1 = round(price - 8, 2)
        tp2 = round(price - 16, 2)
        tp3 = round(price - 28, 2)

    y = 250
    draw.text((W//2, y), "СУХОЙ - XAUUSD", fill=(212,175,55), font=font_1, anchor="mm")
    y += 180
    draw.text((W//2, y), f"{direction}", fill=color, font=font_2, anchor="mm")
    y += 120
    draw.text((W//2, y), f"XAUUSD {price}", fill=color, font=font_3, anchor="mm")
    y += 140
    draw.text((W//2, y), f"ENTRY: {price}", fill="white", font=font_3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"SL: {sl}", fill="white", font=font_3, anchor="mm")
    y += 120
    draw.text((W//2, y), f"TP1: {tp1}", fill=color, font=font_3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"TP2: {tp2}", fill=color, font=font_3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"TP3: {tp3}", fill=color, font=font_3, anchor="mm")

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=98)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start','remove','dry','signal','buy','sell'])
def cmd(m):
    bot.send_message(m.chat.id, "✅", reply_markup=ReplyKeyboardRemove())
    price = get_price()
    direction = random.choice(["BUY", "SELL"])
    if m.text and "buy" in m.text.lower(): direction = "BUY"
    if m.text and "sell" in m.text.lower(): direction = "SELL"
    img = make_signal(price, direction)
    bot.send_photo(m.chat.id, img, caption=f"👑 {direction} {price} | SL | TP1 TP2 TP3")

@
