import os
import io
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    return 4128.7

def make_signal(price, direction):
    W = 1080
    H = 1350
    img = Image.new('RGB', (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=(15,15,15))
    draw.rectangle([10, 10, W-10, H-10], outline=(212,175,55), width=10)
    # Цветной блок вместо текста - чтобы не было ошибки с draw.text
    if direction == 'BUY':
        draw.rectangle([200, 400, 880, 650], fill=(0,255,100))
    else:
        draw.rectangle([200, 400, 880, 650], fill=(255,60,60))
    draw.rectangle([200, 700, 880, 900], fill=(50,50,50))
    draw.rectangle([200, 950, 880, 1150], fill=(212,175,55))
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=90)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start'])
def h_start(m):
    bot.send_message(m.chat.id, 'Bot LIVE! Rabotaet! Pishi /signal', reply_markup=ReplyKeyboardRemove())

@bot.message
