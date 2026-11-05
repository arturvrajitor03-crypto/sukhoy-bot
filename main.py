import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "SUHOY BIG NUMBERS ONLY"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4120.8

def make_image(entry, sl, tp1, tp2, tp3):
    try:
        base = Image.open("template.jpg").convert("RGB")
        w, h = base.size
        base = base.resize((w*3, h*3))
        w, h = base.size
    except:
       
