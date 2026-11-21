import os
import random
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

TOKEN = os.environ.get("BOT_TOKEN") or "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
print(f"TOKEN exists: {bool(os.environ.get('BOT_TOKEN'))}", flush=True)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def kb_main():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("📊 Сигнал", callback_data="signal"))
    m.add(telebot.types.InlineKeyboardButton("📈 Аналитика", callback_data="analytics"),
          telebot.types.InlineKeyboardButton("📰 Новости", callback_data="news"))
    m.add(telebot.types.InlineKeyboardButton("💎 VIP", callback_data="vip"),
          telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="help"))
    return m

def kb_back():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return m

def font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_signal_from_template(direction, price, sl, tp1, tp2, tp3, sila=70):
    try:
        img = Image.open("template.jpg").convert("RGB")
    except Exception as e:
        print(f"template fail: {e}", flush=True)
        return None
    W, H = img.size
    draw = ImageDraw.Draw(img)
    if direction == "BUY":
        col = (0, 170, 80); arrow = "▲  BUY"
    elif direction == "SELL":
        col = (220, 30, 30); arrow = "▼  SELL"
    else:
        col = (180, 150, 40); arrow = "⏳  WAIT"
    x0,
