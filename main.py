import os, requests, random, threading, time
from flask import Flask, request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

# Хранилище активных сделок
active_trades = {}  # chat_id -> {direction, tp1, tp2, tp3, sl, entry_price, hit_tp}

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get("price", 0))
        if price > 1000: return price
    except: pass
    return round(random.uniform(3928, 3952), 2)

def analyze_market(price):
    if price > 3938:
        direction = "SELL"
        entry = f"ниже {price:.0f}"
        sl = int(price + 9)
        tp1 = int(price - 4)
        tp2 = int(price - 8)
        tp3 = int(price - 13)
        analysis = f"Сопротивление {price}$. SELL."
    else:
        direction = "BUY"
        entry = f"выше {price:.0f}"
        sl = int(price - 9)
        tp1 = int(price + 4)
        tp2 = int(price + 8)
        tp3 = int(price + 13)
        analysis = f"Поддержка {price}$. BUY."
    return direction, entry, sl, tp1, tp2, tp3, analysis, price

def find_template():
    for f in os.listdir("."):
        if f.lower().endswith((".jpg",".jpeg",".png",".webp")):
            if "main" not in f.lower():
                return f
    return None

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def create_signal_image(template_path, direction, entry, sl, tp1, tp2, tp3, hit_tps=[]):
    base = Image.open(template_path).convert("RGB").resize((1200, 1900))
    draw = ImageDraw.Draw(base)
    font_big = get_font(82)
    font_mid = get_font(50)
    
    color_dir = (255, 30, 30) if direction == "SELL" else (0, 255, 90)
    
    draw.rectangle([0, 520, 1200, 670], fill=(0,0,0))
    text_dir = f"XAUUSD - {direction}"
    bbox = draw.textbbox((0,0), text_dir, font=font_big)
    w = bbox[2]-bbox[0]
    draw.text(((1200-w)//2, 550), text_dir, font=font_big, fill=color_dir)
    
    draw.rectangle([130, 1330, 1070, 1740], fill=(0,0,0))
    draw.rectangle([130, 1330, 1070, 1740], outline=(212,175,55), width=2)
    
    # Формируем строки с галочками если ТП достигнут
    tp1_mark = "✅" if 1 in hit_tps else "⬜"
    tp2_mark = "✅" if 2 in hit_tps else "⬜"
    tp3_mark = "✅" if 3 in hit_tps else "⬜"
    
    lines = [
        f"Вход: {entry}",
        f"SL: {sl}",
        f"TP1: {tp1}  {tp1_mark}",
        f"TP2: {tp2}  {tp2_mark}",
        f"TP3: {tp3}  {tp3_mark}"
    ]
    
    y = 1345
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_mid)
        w = bbox[2]-bbox[0]
        draw.text(((1200-w)//2, y), line, font=font_mid, fill=(255,235,180))
        y += 70
    
    output_path = f"/tmp/signal_{random.randint(1,9999)}.jpg"
    base.save(output_path, quality=95)
    return output_path

def send_photo(chat_id, photo_path, caption):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
            requests.post(url, data=data, files=files, timeout=25)
    except Exception as e:
        print(f"ERR {e}")

def send_text(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def check_tps_loop():
    # Фоновая проверка ТП каждые 60 секунд
    while True:
        try:
            time.sleep(60)
            if not active_trades:
                continue
            current_price = get_gold_price()
            for chat_id, trade in list(active_trades.items()):
                direction = trade['direction']
