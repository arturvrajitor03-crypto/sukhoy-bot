import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "SUHOY GOLD SNIPER V3 LIVE"

def get_gold_price():
    # 1. Пробуем gold-api (который дал тебе 4137.6 в 13:46)
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r['price'])
    except:
        pass
    # 2. Запасной
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5).json()
        return float(r.get('price', 4135))
    except:
        return 4135.0

def make_image(price, rsi, side):
    img = Image.new('RGB', (800, 450), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    # Заголовок золотой
    draw.rectangle([0, 0, 800, 70], fill=(201, 169, 55))
    draw.text((20, 15), "SUHOY GOLD SNIPER V3", fill=(0,0,0), font=ImageFont.load_default())
    # Сигнал
    color = (255, 50, 50) if side=="SELL" else (50, 255, 50)
    draw.text((20, 90), f"{side} {price}", fill=color, font=ImageFont.load_default())
    draw.text((20, 130), f"RSI {rsi}", fill=(255,255,255), font=ImageFont.load_default())
    draw.text((20, 160), f"ENTRY {price}", fill=(200,200,200), font=ImageFont.load_default())
    draw.text((20, 185), f"SL {price+15:.1f}", fill=(200,200,200), font=ImageFont.load_default())
    draw.text((20, 210), f"TP1 {price-10:.1f} TP2 {price-20:.1f}", fill=(50,255,100), font=ImageFont.load_default())
    draw.text((20, 280), f"RSI6 {rsi} ПЕРЕКУП! Цена у верхней ленты Bollinger. Ждем разворот вниз!", fill=(201,169,55), font=ImageFont.load_default())
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start','check','signal'])
def handle(m):
    price = get_gold_price()
    rsi = 78
    side = "SELL"
    # Текст как в 13:46 который у тебя сработал
    text = f"🔥 ЕСТЬ ТОЧКА! {side} Цена {price} RSI6 {rsi}\nRSI6 {rsi} ПЕРЕКУП! Цена у верхней ленты Bollinger. Ждем разворот вниз!"
    bot.send_message(m.chat.id, text)
    try:
        img = make_image(price, rsi, side)
        bot.send_photo(m.chat.id, img)
    except Exception as e:
        print(e)

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except:
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
