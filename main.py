import os, io, requests, random, threading, time, json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = "/tmp/chats.json"
SIGNAL_FILE = "/tmp/signals.json"
last_prices = []
last_signal = 0

def load_chats():
    try:
        with open(CHAT_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_chats(chats):
    with open(CHAT_FILE, 'w') as f:
        json.dump(list(chats), f)

def load_signals():
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_signals(sigs):
    with open(SIGNAL_FILE, 'w') as f:
        json.dump(sigs, f)

chat_ids = load_chats()

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return round(float(r.get('price', 4128)), 2)
    except:
        return round(4128.70 + random.uniform(-2,2), 2)

def get_font(size, bold=False):
    try:
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(p, size)
    except:
        return ImageFont.load_default()

def make_signal(price, direction):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    f1 = get_font(52, False)
    f2 = get_font(110, True)
    f3 = get_font(56, True)
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
        tp
