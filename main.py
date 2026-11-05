import os, io, requests, random, threading, time
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Список чатов - сохраняем в памяти
CHATS = set()
last_price = 4128.70
last_signal = 0

def get_price():
    global last_price
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        last_price = round(float(r.get('price', last_price)), 2)
        return last_price
    except:
        last_price = round(last_price + random.uniform(-2,2), 2)
        return last_price

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_signal(price, direction):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    f1 = get_font(60, False)
    f2 = get_font(110, True)
    f3 = get_font(58, True)
    
    if direction == "BUY":
        color = (0, 255, 100)
        sl = round(price - 8.5, 2)
        tp1 = round(price + 8, 2)
        tp2 = round(price + 16, 2)
        tp3 = round(price + 28, 2)
    else:
        color = (255, 80, 80)
        sl = round(price + 8.5, 2)
        tp1 = round(price -
