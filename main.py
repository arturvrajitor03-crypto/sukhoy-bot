import os, io
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import requests

TOKEN = "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5).json()
        return float(r['price'])
    except:
        return 4128.7

def make_image(side, entry):
    W = 800
    H = 900
    img = Image.new('RGB', (W, H), (11, 11, 11))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5,5,W-5,H-5], outline=(212,175,55), width=3)
    font_big = ImageFont.load_default()
    font_med = ImageFont.load_default()
    col = (50,255,100) if side == "BUY" else (255,60,60)
    draw.text((400
