import os, requests, threading, random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
fapp = Flask(__name__)
@fapp.route('/')
def home(): return "BOT ALIVE"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return int(float(r.get("price", 4065)))
    except:
        return 4065

def make_card(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (600, 850), (15, 15, 15))
    d = ImageDraw.Draw(img)
    d.rectangle([5,5,595,845], outline=(212,175,55), width=4)
    f = ImageFont.load_default()
    col = (255,70,70) if direction=="SELL" else (70,255,70)
    d.text((110,30), f"SUHOY - XAUUSD", fill=(212,175,55), font=f)
    d.text((150,80), f"{direction} {entry}$", fill=col, font=f)
    d.text((260,200), "BULL", fill=(212,175,55), font=f)
    d.text((150,400), f"Entry below {entry}", fill="white", font=f)
    d.text((180,440), f"SL: {sl}", fill="white", font=f)
    d.text((150,480), f"TP1: {tp1}", fill="white", font=f)
    d.text((150,510), f"TP2: {tp2}", fill="white", font=f)
    d.text((150,540), f"TP3: {tp3}", fill="white", font=f)
    img.save("card.jpg")
    return "card.jpg"

async def dry(update, context):
    p = get_price()
    direction = random.choice(["SELL","BUY"])
    if direction=="SELL":
        sl, tp1, tp2, tp3 = p+9, p-4, p-8, p-13
    else:
       
