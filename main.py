import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
@app.route('/')
def home():
    return "FINAL CLEAN"
def get_price():
    try:
        return float(requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()["price"])
    except:
        return 4123.0
def make_image(e, sl, t1, t2, t3):
    w = 1200
    h = 1400
    img = Image.new("RGB", (w, h), (10, 10, 10))
    d = ImageDraw.Draw(img)
    d.rectangle((5, 5, w-5, h-5), outline=(255, 215, 0), width=15)
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    d.text((w//2, 300), "SELL", fill=(255, 30, 30), font=f1, anchor="mm")
    d.text((w//2, 500), f"{e:.2f}", fill=(255, 255, 255), font=f1, anchor="mm")
    d.text((w//2, 700), f"SL {sl:.0f}", fill=(255, 100, 100), font=f2, anchor="mm")
    d.text((w//2, 850), f"TP1 {t1:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    d.text((w//2, 1000), f"TP2 {t2:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    d.text((w//2, 1150), f"TP3 {t3:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    bio = BytesIO()
    img.save(bio, "JPEG", quality=90)
    bio.seek(0)
    return bio
@bot.message_handler(commands=["start", "check"])
def h(m):
    p = get_price()
    im = make_image(p, p+12, p-10, p-20, p-35)
    bot.send_photo(m.chat.id, im, caption="SUHOY SNIPER SELL")
def run():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling()
        except:
            time.sleep(5)
threading.Thread(target=run, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
