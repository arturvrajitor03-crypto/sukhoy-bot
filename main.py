import os
import io
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    return 4128.7

def make_signal(price, direction):
    W = 1080
    H = 1350
    img = Image.new('RGB', (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    gold = (212, 175, 55)
    draw.rectangle([12, 12, W-12, H-12], outline=gold, width=8)

    try:
        fp = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        fpb = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        f_small = ImageFont.truetype(fp, 52)
        f_big = ImageFont.truetype(fpb, 110)
        f_mid = ImageFont.truetype(fp, 56)
    except:
        f_small = ImageFont.load_default()
        f_big = ImageFont.load_default()
        f_mid = ImageFont.load_default()

    if direction == 'BUY':
        col = (0, 255, 100)
        sl = price - 8.5
        tp1 = price + 8
        tp2 = price + 16
        tp3 = price + 28
    else:
        col = (255, 80, 80)
        sl = price + 8.5
        tp1 = price - 8
        tp2 = price - 16
        tp3 = price - 28

    xc = W // 2
    y = 250
    pos = (xc, y)
    draw.text(pos, 'SUHOY - XAUUSD', fill=gold, font=f_small, anchor='mm')
    y = y + 180
    pos = (xc, y)
    draw.text(pos, direction, fill=col, font=f_big, anchor='mm')
    y = y + 120
    pos = (xc, y)
    txt = 'XAUUSD ' + str(price)
    draw.text(pos, txt, fill
