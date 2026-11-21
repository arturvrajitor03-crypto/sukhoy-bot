import os
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN") or "123456:ABC"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            return ImageFont.load_default()

def pic(direct, price, sl, tp1, tp2, tp3, sila):
    if os.path.exists("template.jpg"):
        img = Image.open("template.jpg").convert("RGB")
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

    draw.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(255, 255, 255))
    draw.rounded_rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], radius=25, outline=(212, 175, 55), width=3)

    cx = W // 2
    f_big = get_font(int(W * 0.09))
    f_mid = get_font(int(W * 0.055))
    f_small = get_font(int(W * 0.05))

    draw.text((cx, y0 + int(H * 0.03)), arr, font=f_big, fill=col, anchor="mm")
    draw.text((cx, y0 + int(H * 0.075)), "Sila: " + str(sila) + "%", font=f_small, fill=(180, 140, 20), anchor
