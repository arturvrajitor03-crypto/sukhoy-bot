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
    try:
        with open(CHAT_FILE, 'w') as f:
            json.dump(list(chats), f)
    except:
        pass

def load_signals():
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_signals(sigs):
    try:
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(sigs, f)
    except:
        pass

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
    return bio, {"entry": price, "dir": direction, "tp1": tp1, "tp2": tp2, "tp3": tp3, "sl": sl, "hit": []}

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
            new_signals = []
            for sig in signals:
                hit = sig.get("hit", [])
                msg = None
                if sig["dir"] == "BUY":
                    if price >= sig["tp1"] and "tp1" not in hit:
                        hit.append("tp1")
                        msg = "GAlochka TP1 proiden! BUY " + str(sig["entry"]) + " -> " + str(sig["tp1"]) + " Cena " + str(price)
                    elif price >= sig["tp2"] and "tp2" not in hit:
                        hit.append("tp2")
                        msg = "GAlochka TP2 proiden! BUY " + str(sig["entry"]) + " -> " + str(sig["tp2"]) + " Cena " + str(price)
                    elif price >= sig["tp3"] and "tp3" not in hit:
                        hit.append("tp3")
                        msg = "GAlochka TP3 proiden! BUY " + str(sig["entry"]) + " -> " + str(sig["tp3"]) + " Cena " + str(price)
                    if price <= sig["sl"] and "sl" not in hit:
                        hit.append("sl")
                        msg = "Stop Loss " + str(sig["entry"])
                else:
                    if price <= sig["tp1"] and "tp1" not in hit:
                        hit.append("tp1")
                        msg = "GAlochka TP1 proiden! SELL " + str(sig["entry"]) + " -> " + str(sig["tp1"]) + " Cena " + str(price)
                    elif price <= sig["tp2"] and "tp2" not in hit:
                        hit.append("tp2")
                        msg = "GAlochka TP2 proiden! SELL " + str(sig["entry"]) + " -> " + str(sig["tp2"]) + " Cena " + str(price)
                    elif price <= sig["tp3"] and "tp3" not in hit:
                        hit.append("tp3")
                        msg = "GAlochka TP3 proiden! SELL " + str(sig["entry"]) + " -> " + str(sig["tp3"]) + " Cena " + str(price)
                    if price >= sig["sl"] and "sl" not in hit:
                        hit.append("sl")
                        msg = "Stop Loss " + str(sig["entry"])
                if msg:
                    chat_ids = load_chats()
                    for cid in list(chat_ids):
                        try:
                            bot.send_message(cid, msg)
                        except:
                            pass
                sig["hit"] = hit
                if len(hit) < 3 and "sl" not in hit:
                    new_signals.append(sig)
            save_signals(new_signals)
            if len(last_prices) >= 10:
                avg = sum(last_prices[:-1]) / (len(last_prices)-1)
                diff = price - avg
                signal = None
                if diff < -3.0:
                    signal = "BUY"
                elif diff > 3.0:
                    signal = "SELL"
                chat_ids = load_chats()
                if signal and (time.time() - last_signal > 900) and chat_ids:
                    img, sig_data = make_signal(price, signal)
                    signals = load_signals()
                    signals.append(sig_data)
                    save_signals(signals)
                    for cid in list(chat_ids):
                        try:
                            bot.send_photo(cid, img, caption="Vxod " + signal + " " + str
