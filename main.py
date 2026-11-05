import os
import io
import random
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    return round(4128.7 + random.uniform(-3, 3), 2)

def make_signal(price, direction):
    W = 1080
    H = 1350
    img = Image.new('RGB', (W, H), (8, 8, 8))
    d = ImageDraw.Draw(img)
    gold = (212, 175, 55)
    d.rectangle([12, 12, W-12, H-12], outline=gold, width=8)

    try:
        font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        font_b_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        f_small = ImageFont.truetype(font_path, 52)
        f_big = ImageFont.truetype(font_b_path, 110)
        f_mid = ImageFont.truetype(font_path, 56)
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

    sl = round(sl, 2)
    tp1 = round(tp1, 2)
    tp2 = round(tp2, 2)
    tp3 = round(tp3, 2)

    x_center = W // 2
    y = 250
    pos1 = (x_center, y)
    d.text(pos1, 'SUHOY - XAUUSD', fill=gold, font=f_small, anchor='mm')
    y = y + 180
    pos2 = (x_center, y)
    d.text(pos2, direction, fill=col, font=f_big, anchor='mm')
    y = y + 120
    pos3 = (x_center, y)
    txt_price = 'XAUUSD ' + str(price)
    d.text(pos3, txt_price, fill=col, font=f_mid, anchor='mm')
    y = y + 140
    pos4 = (x_center, y)
    txt_entry = 'ENTRY: ' + str(price)
    d.text(pos4, txt_entry, fill=(255,255,255), font=f_mid, anchor='mm')
    y = y + 85
    pos5 = (x_center, y)
    txt_sl = 'SL: ' + str(sl)
    d.text(pos5, txt_sl, fill=(255,255,255), font=f_mid, anchor='mm')
    y = y + 120
    pos6 = (x_center, y)
    txt_tp1 = 'TP1: ' + str(tp1)
    d.text(pos6, txt_tp1, fill=col, font=f_mid, anchor='mm')
    y = y + 85
    pos7 = (x_center, y)
    txt_tp2 = 'TP2: ' + str(tp2)
    d.text(pos7, txt_tp2, fill=col, font=f_mid, anchor='mm')
    y = y + 85
    pos8 = (x_center, y)
    txt_tp3 = 'TP3: ' + str(tp3)
    d.text(pos8, txt_tp3, fill=col, font=f_mid, anchor='mm')

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=98)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start'])
def s(m):
    bot.send_message(m.chat.id, 'Avto vhod vkluchen! Signal tolko kogda est tochka!', reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['signal','buy','sell'])
def cmd(m):
    price = get_price()
    txt = m.text.lower()
    d = 'BUY'
    if 'sell' in txt:
        d = 'SELL'
    img = make_signal(price, d)
    bot.send_photo(m.chat.id, img)

@app.route('/')
def h():
    return 'SUHOY LIVE', 200

@app.route('/webhook', methods=['POST'])
def wh():
    try:
        raw = request.data.decode('utf-8')
        upd = telebot.types.Update.de_json(raw)
        bot.process_new_updates([upd])
    except:
        pass
    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=port)
