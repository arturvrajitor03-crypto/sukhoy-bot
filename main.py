import os, io, random
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

def make_signal_image(side="BUY", entry=4128.7):
    W, H = 800, 1000
    img = Image.new('RGB', (W, H), (11, 11, 11))
    draw = ImageDraw.Draw(img)
    
    # Золотая рамка
    draw.rectangle([5,5,W-5,H-5], outline=(212,175,55), width=3)
    draw.rectangle([15,15,W-15,H-15], outline=(212,175,55), width=1)

    # Заголовок
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        font_med = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 30)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Бык
    draw.text((W//2, 90), "🐂", font=font_big, anchor="mm", fill=(212,175,55))
    draw.text((W//2, 160), f"{side} XAUUSD", font=font_big, anchor="mm", fill=(212,175,55) if side=="BUY" else (255,70,70))
    
    price = entry
    sl = price - 12 if side=="BUY" else price + 12
    tp1 = price + 8 if side=="BUY" else price - 8
    tp2 = price + 16 if side=="BUY" else price - 16
    tp3 = price + 28 if side=="BUY" else price - 28

    y = 240
    def line(label, val, color=(255,255,255)):
        nonlocal y
        draw.text((60, y), label, font=font_med, fill=(160,160,160))
        draw.text((W-60, y), f"{val:.1f}", font=font_med, anchor="rm", fill=color)
        y+=70

    line("ENTRY:", price, (255,255,255))
    line("SL:", sl, (255,80,80))
    y+=20
    line("TP1:", tp1, (50,255,100))
    line("TP2:", tp2, (50,255,100))
    line("TP3:", tp3, (50,255,100))

    # Линия графика фальш
    y+=60
    draw.line([(60,y),(W-60,y+120),(W//2,y+60),(W-60,y+180)], fill=(212,175,55), width=4)
    
    y+=250
    draw.text((W//2, y), "SUHOY GOLD SIGNALS", font=font_small, anchor="mm", fill=(212,175,55))

    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio, price, sl, tp1, tp2, tp3

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bot LIVE! Pishi /signal\n\nCommands:\n/signal - Gold signal\n/buy - Buy\n/sell - Sell")

@bot.message_handler(commands=['signal','buy','sell'])
def signal(m):
    cmd = m.text.replace('/','').lower()
    side = "BUY" if cmd in ['signal','buy'] else "SELL"
    if cmd=="signal":
        side = random.choice(["BUY","SELL"])
    
    entry = get_price()
    img_bio, price, sl, tp1, tp2, tp3 = make_signal_image(side, entry)
    
    caption = f"{side} XAUUSD {price:.1f}\n\nENTRY: {price:.1f}\nSL: {sl:.1f}\n\nTP1: {tp1:.1f}\nTP2: {tp2:.1f}\nTP3: {tp3:.1f}"
    bot.send_photo(m.chat.id, img_bio, caption=caption)

@app.route('/', methods=['GET'])
def home():
    return "SUHOY LIVE GOLD"

@app.route('/webhook', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
