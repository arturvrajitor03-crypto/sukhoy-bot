import os, io, requests, random
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4115))
    except:
        return 4115.89

def make_signal(price, direction):
    base = Image.open("template.jpg").convert("RGB")
    W,H = base.size
    draw = ImageDraw.Draw(base)
    try:
        f1 = ImageFont.truetype("arial.ttf", int(H*0.065))
        f2 = ImageFont.truetype("arial.ttf", int(H*0.042))
    except:
        f1 = ImageFont.load_default(); f2 = f1

    if direction == "BUY":
        sl = round(price-8,2)
        tp1 = round(price+8,2); tp2 = round(price+16,2); tp3 = round(price+28,2)
        color = (0,255,100)
    else:
        sl = round(price+8,2)
        tp1 = round(price-8,2); tp2 = round(price-16,2); tp3 = round(price-28,2)
        color = (255,70,70)

    y = int(H*0.32)
    draw.rectangle([0, y-20, W, y+int(H*0.48)], fill=(0,0,0))
    draw.text((W*0.08, y), f"СУХОЙ - XAUUSD", fill=(210,180,120), font=f2)
    draw.text((W*0.08, y+int(H*0.06)), f"{direction} XAUUSD", fill=color, font=f1)
    draw.text((W*0.08, y+int(H*0.15)), f"ENTRY: {price}", fill="white", font=f2)
    draw.text((W*0.08, y+int(H*0.21)), f"SL: {sl}", fill="white", font=f2)
    draw.text((W*0.08, y+int(H*0.27)), f"TP1: {tp1}\nTP2: {tp2}\nTP3: {tp3}", fill=color, font=f2)
    
    bio = io.BytesIO()
    base.save(bio, format='JPEG', quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start','remove','dry','signal'])
def start_cmd(m):
    bot.send_message(m.chat.id, "✅ Кнопки убраны!", reply_markup=ReplyKeyboardRemove())
    price = get_price()
    direction = random.choice(["BUY","SELL"])
    img = make_signal(price, direction)
    bot.send_photo(m.chat.id, img, caption=f"{direction} {price} TP1/TP2/TP3")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    text = m.text.upper() if m.text else ""
    if "BUY" in text:
        img = make_signal(get_price(), "BUY")
        bot.send_photo(m.chat.id, img, reply_markup=ReplyKeyboardRemove())
    elif "SELL" in text:
        img = make_signal(get_price(), "SELL")
        bot.send_photo(m.chat.id, img, reply_markup=ReplyKeyboardRemove())

@app.route('/')
def h(): return "TP1 TP2 TP3 READY",200
@app.route('/webhook', methods=['POST'])
def wh():
    u = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([u]); return 'ok',200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
