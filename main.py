import os, io, requests, random, threading, time
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont
from collections import deque

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = "/tmp/chat_ids.txt"
price_history = deque(maxlen=50)  # храним последние цены

def save_chat_id(chat_id):
    try:
        ids = set()
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f: ids = set(f.read().split())
        ids.add(str(chat_id))
        with open(CHAT_FILE, "w") as f: f.write("\n".join(ids))
    except: pass

def get_chat_ids():
    try:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                return [int(x) for x in f.read().split() if x.strip()]
    except: pass
    return []

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = round(float(r.get('price', 4128)), 2)
        price_history.append(price)
        return price
    except:
        p = round(4128.70 + random.uniform(-3,3), 2)
        price_history.append(p)
        return p

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except: continue
    return ImageFont.load_default()

def make_signal(price, direction, reason):
    W, H = 1080, 1350
    img = Image
