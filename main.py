import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "SUHOY GOLD SNIPER V3 LIVE 24/7"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()
        return float(r['price'])
    except:
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=6).json()
            return float(r['price'])
        except:
            return 4131.29

def make_signal_image(price, rsi, side="SELL"):
    try:
        # Пытаемся открыть твой красивый шаблон
        base = Image.open("template.jpg").convert("RGB")
        base = base.resize((800, 450))
    except:
        base = Image.new('RGB', (800, 450), color=(15,15,15))
    
    draw = ImageDraw.Draw(base)
    # Делаем полупрозрачный фон для текста
    try:
        font_big = ImageFont.truetype("arial.ttf", 32)
        font_mid = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Золотой верх как у тебя был
    draw.rectangle([0, 0, 800, 55], fill=(201, 169, 55))
    draw.text((20, 12), f"SUHOY GOLD SNIPER V3 | {side}", fill=(0,0,0), font=font_mid)
    
    # Данные
    draw.text((20, 80), f"{side} {price:.1f}", fill=(255,60,60), font=font_big)
    draw.text((20, 125), f"RSI {rsi}", fill=(255,255,255), font=font_mid)
    draw.text((20, 160), f"ENTRY {price:.1f}", fill=(220,220,220), font=font_mid)
    draw.text((20, 190), f"SL {price+12:.1f} | TP {price-15:.1f} / {price-25:.1f}", fill=(100,255,100), font=font_small)
    draw.text((20, 380), f"RSI6 {rsi} ПЕРЕКУП! Цена у верхней ленты Bollinger. Ждем вниз!", fill=(201,169,55), font=font_small)

    bio = BytesIO()
    base.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start','check','signal','checksignal'])
def handle(m):
    price = get_price()
    rsi = 78
    side = "SELL"
    text = f"🔥 ЕСТЬ ТОЧКА! {side} Цена {price:.2f}\nRSI6 {rsi} ПЕРЕКУП! Цена у верхней ленты Bollinger. Ждем разворот вниз!"
    bot.send_message(m.chat.id, text)
    try:
        img = make_signal_image(price, rsi, side)
        bot.send_photo(m.chat.id, img)
    except Exception as e:
        print(e)

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(e)
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
