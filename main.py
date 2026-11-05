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
        return 4128.70

def make_signal(price, direction):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
        f3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
    except:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()
        f3 = ImageFont.load_default()
    if direction == "BUY":
        color = (0, 255, 100)
        sl = price - 8.5
        tp
