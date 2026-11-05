import os, io, requests, random, threading, time, json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = "/tmp/chats.json"
SIGNAL_FILE = "/tmp/signals.json"
last_prices = []
last_signal = 0

def load_chats():
    try:
        with open(CHAT_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_chats(chats):
    with open(CHAT_FILE, 'w') as f:
        json.dump(list(chats), f)

def load_signals():
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_signals(sigs):
    with open(SIGNAL_FILE, 'w') as f:
        json.dump(sigs, f)

chat_ids = load_chats()

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return round(float(r.get('price', 4128)), 2)
    except:
        return round(4128.70 + random.uniform(-2,2), 2)

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_signal(price, direction):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    f1 = get_font(52, False)
    f2 = get_font(110, True)
    f3 = get_font(56, True)
    if direction == "BUY":
        color = (0, 255, 100)
        sl = round(price - 8.5, 2)
        tp1 = round(price + 8, 2)
        tp2 = round(price + 16, 2)
        tp3 = round(price + 28, 2)
    else:
        color = (255, 80, 80)
        sl = round(price + 8.5, 2)
        tp1 = round(price - 8, 2)
        tp2 = round(price - 16, 2)
        tp3 = round(price - 28, 2)
    y = 250
    draw.text((W//2, y), "SUHOY - XAUUSD", fill=(212,175,55), font=f1, anchor="mm")
    y += 180
    draw.text((W//2, y), direction, fill=color, font=f2, anchor="mm")
    y += 120
    draw.text((W//2, y), f"XAUUSD {price}", fill=color, font=f3, anchor="mm")
    y += 140
    draw.text((W//2, y), f"ENTRY: {price}", fill="white", font=f3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"SL: {sl}", fill="white", font=f3, anchor="mm")
    y += 120
    draw.text((W//2, y), f"TP1: {tp1}", fill=color, font=f3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"TP2: {tp2}", fill=color, font=f3, anchor="mm")
    y += 85
    draw.text((W//2, y), f"TP3: {tp3}", fill=color, font=f3, anchor="mm")
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=98)
    bio.seek(0)
    return bio, [sl, tp1, tp2, tp3]

def auto_checker():
    global last_prices, last_signal, chat_ids
    time.sleep(30)
    while True:
        try:
            price = get_price()
            last_prices.append(price)
            if len(last_prices) > 20:
                last_prices.pop(0)
            signals = load_signals()
            keep = []
            for sig in signals:
                entry = sig["entry"]
                d = sig["dir"]
                tp1 = sig["tp1"]
                tp2 = sig["tp2"]
                tp3 = sig["tp3"]
                hit = sig["hit"]
                msg = ""
                if d == "BUY":
                    if price >= tp1 and "tp1" not in hit:
                        hit.append("tp1")
                        msg = "Galochka TP1 proyden! BUY " + str(entry) + " -> " + str(tp1)
                    if price >= tp2 and "tp2" not in hit:
                        hit.append("tp2")
                        msg = "Galochka TP2 proyden! BUY " + str(entry) + " -> " + str(tp2)
                    if price >= tp3 and "tp3" not in hit:
                        hit.append("tp3")
                        msg = "Galochka TP3 proyden! BUY " + str(entry) + " -> " + str(tp3)
                else:
                    if price <= tp1 and "tp1" not in hit:
                        hit.append("tp1")
                        msg = "Galochka TP1 proyden! SELL " + str(entry) + " -> " + str(tp1)
                    if price <= tp2 and "tp2" not in hit:
                        hit.append("tp2")
                        msg = "Galochka TP2 proyden! SELL " + str(entry) + " -> " + str(tp2)
                    if price <= tp3 and "tp3" not in hit:
                        hit.append("tp3")
                        msg = "Galochka TP3 proyden! SELL " + str(entry) + " -> " + str(tp3)
                if msg != "":
                    cids = load_chats()
                    for cid in list(cids):
                        try:
                            bot.send_message(cid, msg)
                        except:
                            pass
                sig["hit"] = hit
                if len(hit) < 3:
                    keep.append(sig)
            save_signals(keep)
            if len(last_prices) >= 10:
                avg = sum(last_prices[:-1]) / (len(last_prices)-1)
                diff = price - avg
                sig_type = None
                if diff < -3.0:
                    sig_type = "BUY"
                if diff > 3.0:
                    sig_type = "SELL"
                cids = load_chats()
                if sig_type and (time.time() - last_signal > 900) and cids:
                    img, vals = make_signal(price, sig_type)
                    new_sig = {"entry": price, "dir": sig_type, "sl": vals[0], "tp1": vals[1], "tp2": vals[2], "tp3": vals[3], "hit": []}
                    all_sigs = load_signals()
                    all_sigs.append(new_sig)
                    save_signals(all_sigs)
                    for cid in list(c
