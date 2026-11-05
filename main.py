import os
import io
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    TOKEN = '123456:TEST'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def make_img():
    W = 1080
    H = 1350
    img = Image.new('RGB', (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 12, W-12, H-12], outline=(212, 175, 55), width=8)
    try:
        f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 50)
        f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
    except:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()
    draw.text((300, 300), 'SUHOY XAUUSD', fill=(212, 175, 55), font=f1)
    draw.text((400, 600),
