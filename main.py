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
        return round(float(r.get('price', 4125)), 2)
    except:
        return round(4125.29 + random.uniform(-2,2), 2)

def make_signal(price, direction):
    # Создаем чистую картинку с нуля - 1080x1350, черная + золотая рамка
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # Золотая рамка
    draw.rectangle([15,15,W-15,H-15], outline=(212,175,55), width=6)
    draw.rectangle([30,30,W-30,H-30], outline=(212,175,55), width=2)
    
    try:
        # Пробуем загрузить шрифт
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_big = ImageFont.truetype("arialbd.ttf", 95)
        font_mid = ImageFont.truetype("arial.ttf", 52)
        font_small = ImageFont.truetype("arial.ttf", 38)
    except:
        font_title = ImageFont.load_default()
        font_big = font_title
        font_mid = font_title
        font_small = font_title

    if direction == "BUY":
        color = (0, 255, 90)
        sl = round(price - 8.5, 2)
        tp1 = round(price + 8, 2)
        tp2 = round(price + 16, 2)
        tp3 = round(price + 28, 2)
    else:
        color = (255, 70, 70)
        sl = round(price + 8.5, 2)
        tp1 = round(price - 8, 2)
        tp2 = round(price - 16, 2)
        tp3 = round(price - 28, 2)

    # Текст крупно по центру
    y = 280
    draw.text((W//2, y), "СУХОЙ - XAUUSD", fill=(212,175,55), font=font_title, anchor="mm")
    y += 120
    draw.text((W//2, y), f"{direction} XAUUSD", fill=color, font=font_big, anchor="mm")
    y += 140
    draw.text((W//2, y), f"ENTRY: {price}", fill="white", font=font_mid, anchor="mm")
    y += 80
    draw.text((W//2, y), f"SL: {sl}", fill="white", font=font_mid, anchor="mm")
    y += 110
    draw.text((W//2, y), f"TP1: {tp1}", fill=color, font=font_mid, anchor="mm")
    y += 75
    draw.text((W//2, y), f"TP2: {tp2}", fill=color, font=font_mid, anchor="mm")
    y += 75
    draw.text((W//2, y), f"TP3: {tp3}", fill=color, font=font_mid, anchor="mm")
    
    y += 140
    draw.text((W//2, y), "R/R ~ 1:2.6  •  SUHOY SIGNALS", fill=(180,180,180), font=font_small, anchor="mm")

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start','remove','dry','signal','buy','sell'])
def cmd(m):
    bot.send_message(m.chat.id, "✅ Готово!", reply_markup=ReplyKeyboardRemove())
    price = get_price()
    direction = random.choice(["BUY", "SELL"])
    # Если написали buy/sell - слушаем
    if "buy" in m.text.lower(): direction = "BUY"
    if "sell" in m.text.lower(): direction = "SELL"
    img = make_signal(price, direction)
    bot.send_photo(m.chat.id, img, caption=f"👑 {direction} {price}\nSL {round(price-8,2) if direction=='BUY' else round(price+8,2)} | TP1 TP2 TP3")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    if not m.text: return
    txt = m.text.upper()
    if "BUY" in txt or "SELL" in txt or "/SIGNAL" in txt:
        direction = "BUY" if "BUY" in txt else "SELL"
        if "/SIGNAL" in txt: direction = random.choice(["BUY","SELL"])
        img = make_signal(get_price(), direction)
        bot.send_photo(m.chat.id, img, reply_markup=ReplyKeyboardRemove())

@app.route('/')
def h(): return "TP1 TP2 TP3 FIXED",200
@app.route('/webhook', methods=['POST'])
def wh():
    u = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([u]); return 'ok',200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
