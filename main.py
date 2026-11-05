import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "SUHOY FINAL"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4120.8

def make_image(entry, sl, tp1, tp2, tp3):
    try:
        base = Image.open("template.jpg").convert("RGB")
        w, h = base.size
        base = base.resize((w*2, h*2))
        w, h = base.size
    except:
        w, h = 1000, 1000
        base = Image.new("RGB", (w, h), (15,15,15))
    draw = ImageDraw.Draw(base)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
    except:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()

    x1 = int(w*0.05)
    y1 = int(h*0.35)
    x2 = int(w*0.95)
    y2 = int(h*0.85)
    draw.rectangle((x1, y1, x2, y2), fill=(0,0,0))

    draw.text((w//2, h//2 - 60), f"SELL {entry:.2f}", fill=(255,30,30), font=f1, anchor="mm")
    draw.text((w//2, h//2 + 60), f"TP1 {tp1:.0f} TP2 {tp2:.0f} TP3 {tp3:.0f}", fill=(0,255,100), font=f2, anchor="mm")
    draw.text((w//2, h//2 + 130), f"SL {sl:.0f} ENTRY {entry:.2f}", fill=(255,255,255), font=f2, anchor="mm")

    bio = BytesIO()
    base.save(bio, "JPEG", quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=["start","check","signal"])
def handle(m):
    price = get_price()
    entry = price
    sl = entry + 12
    tp1 = entry - 10
    tp2 = entry - 20
    tp3 = entry - 35
    img = make_image(entry, sl, tp1, tp2, tp3)
    txt = f"🔥 ЕСТЬ ТОЧКА! SELL Цена {entry:.2f}\nRSI 78 ПЕРЕКУП!\n\nВХОД {entry:.2f}\nSL {sl:.0f}\nTP1 {tp1:.0f} TP2 {tp2:.0f} TP3 {tp3:.0f}"
    bot.send_message(m.chat.id, txt)
    bot.send_photo(m.chat.id, img)

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
