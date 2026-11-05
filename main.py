import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4120.0

def make_image(entry, sl, tp1, tp2, tp3):
    w = 1200
    h = 1400
    img = Image.new("RGB", (w, h), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle((5, 5, w-5, h-5), outline=(255, 215, 0), width=20)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        f3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    except:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()
        f3 = ImageFont.load_default()
    draw.text((w//2, 250), "SELL", fill=(255, 30, 30), font=f1, anchor="mm")
    draw.text((w//2, 450), f"{entry:.2f}", fill=(255, 255, 255), font=f1, anchor="mm")
    draw.text((w//2, 650), f"SL {sl:.0f}", fill=(255, 100, 100), font=f2, anchor="mm")
    draw.text((w//2, 800), f"TP1 {tp1:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 950), f"TP2 {tp2:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 1100), f"TP3 {tp3:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 100), "SUHOY - XAUUSD", fill=(255, 215, 0), font=f3, anchor="mm")
    bio = BytesIO()
    img.save(bio, "JPEG", quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=["start", "check", "signal"])
def handle(m):
    p = get_price()
    e = p
    sl = e + 12
    t1 = e - 10
    t2 = e - 20
    t3 = e - 35
    im = make_image(e, sl, t1, t2, t3)
    bot.send_photo(m.chat.id, im, caption="SELL")

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
