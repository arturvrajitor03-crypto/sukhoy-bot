import os
import requests
import threading
import random
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")

fapp = Flask(__name__)

@fapp.route('/')
def home():
    return "BOT ALIVE - 4065 FIXED"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get("price", 4065))
        return int(price)
    except:
        return 4065

def make_card(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (600, 850), (15, 15, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 595, 845], outline=(212, 175, 55), width=4)
    font = ImageFont.load_default()
    color = (255, 70, 70) if direction == "SELL" else (70, 255, 70)
    draw.text((110, 30), "SUHOY - XAUUSD", fill=(212, 175, 55), font=font)
    draw.text((150, 80), f"{direction} {entry}$", fill=color, font=font)
    draw.text((260, 200), "BULL", fill=(212, 175, 55), font=font)
    draw.text((150, 400), f"Entry below {entry}", fill="white", font=font)
    draw.text((180, 440), f"SL: {sl}", fill="white", font=font)
    draw.text((150, 480), f"TP1: {tp1}", fill="white", font=font)
    draw.text((150, 510), f"TP2: {tp2}", fill="white", font=font)
    draw.text((150, 540), f"TP3: {tp3}", fill="white", font=font)
    draw.text((120, 650), "Sleju i stavlu", fill=(212, 175, 55), font=font)
    img.save("card.jpg")
    return "card.jpg"

async def dry(update, context):
    p = get_price()
    direction = random.choice(["SELL", "BUY"])
    if direction == "SELL":
        sl = p + 9
        tp1 = p - 4
        tp2 = p - 8
        tp3 = p - 13
    else:
        sl = p - 9
        tp1 = p + 4
        tp2 = p + 8
        tp3 = p + 13
    
    # ФИКС - было f"{p}.100098$" стало f"{p}$"
    caption = f"👑 {direction} {p}$\nTP1 {tp1} ⬜\nTP2 {tp2} ⬜\nTP3 {tp3} ⬜\nSleju i stavlu ✅"
    await update.message.reply_photo(
        photo=open(make_card(direction, p, sl, tp1, tp2, tp3), 'rb'),
        caption=caption
    )

async def start(update, context):
    await update.message.reply_text("Bot works! /dry")

if __name__ == "__main__":
    threading.Thread(target=lambda: fapp.run(host='0.0.0.0', port=10000), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("dry", dry))
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
