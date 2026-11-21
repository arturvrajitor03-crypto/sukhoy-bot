import os
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
APP_URL = APP_URL.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_font(size):
    try:
        f = "DejaVuSans-Bold.ttf"
        return ImageFont.truetype(f, size)
    except:
        try:
            f2 = "/usr/share/fonts/truetype/"
            f2 += "dejavu/DejaVuSans-Bold.ttf"
            return ImageFont.truetype(f2, size)
        except:
            return ImageFont.load_default()

def pic(direct, price, sl, tp1, tp2, tp3, sila):
    if os.path.exists("template.jpg"):
        img = Image.open("template.jpg")
        img = img.convert("RGB")
    else:
        img = Image.new("RGB", (800, 1200), (20, 20, 20))
    W, H = img.size
    draw = ImageDraw.Draw(img)
    if direct == "BUY":
        col = (0, 170, 80)
        arr = "BUY"
    elif direct == "SELL":
        col = (220, 30, 30)
        arr = "SELL"
    else:
        col = (180, 150, 40)
        arr = "WAIT"
    x0 = int(W * 0.08)
    x1 = int(W * 0.92)
    y0 = int(H * 0.60)
    y1 = int(H * 0.96)
    box = 
