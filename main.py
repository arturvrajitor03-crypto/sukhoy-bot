import os, threading, time, requests, telebot, json
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
ACTIVE_FILE = "/tmp/active_signal.json"

@app.route('/')
def home(): return "SUHOY SNIPER TP TRACKER LIVE"

def get_price():
    try: return float(requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()['price'])
    except: return 4130.50

def save_signal(data):
    try:
        with open(ACTIVE_FILE, 'w') as f: json.dump(data, f)
    except: pass

def load_signal():
    try:
        with open(ACTIVE_FILE, 'r') as f: return json.load(f)
    except: return None

def make_image_with_checks(price_now, signal):
    # signal = {entry, sl, tp1,tp2,tp3, side, rsi, hits: [tp1_hit, tp2_hit...]}
    W, H = 1280, 800
    img = Image.new('RGB', (W, H), color=(10,10,10))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,H], outline=(201,169,55), width=10)
    
    try:
        f_huge = ImageFont.truetype("arialbd.ttf", 100)
        f_big = ImageFont.truetype("arialbd.ttf", 55)
        f_mid = ImageFont.truetype("arial.ttf", 28)
    except:
        f_huge = f_big = f_mid = ImageFont.load_default()

    entry = signal['entry']
    sl = signal['sl']
    tp1, tp2, tp3 = signal['tp1'], signal['tp2'], signal['tp3']
    side = signal['side']
    
    # Проверяем какие TP пройдены СЕЙЧАС
    hits = [False, False, False]
    if side == "SELL":
        if price_now <= tp1: hits[0]=True
        if price_now <= tp2: hits[1]=True
        if price_now <= tp3: hits[2]=True
    else:
        if price_now >= tp1: hits[0]=True
        if price_now >= tp2: hits[1]=True
        if price_now >= tp3: hits[2]=True

    draw.text((W//2, 40), "GOLD • XAU/USD • SELL SIGNAL", fill=(201,169,55), font=f_mid, anchor="mt")
    color = (255,30,30) if side=="SELL" else (30,255,90)
    draw.text((W//2, 180), f"{side} {entry:.2f}", fill=color, font=f_huge, anchor="mm")

    y = 350
    draw.text((200, y), f"ENTRY\n{entry:.2f}\nRSI {signal['rsi']}", fill=(255,255,255), font=f_big, anchor="mm", align="center")
    draw.text((W-200, y), f"STOP LOSS\n{sl:.0f}", fill=(255,255,255), font=f_big, anchor="mm", align="center")

    # TP1 TP2 TP3 с галочками
    y = 520
    for i, (tp, hit) in enumerate([(tp1,hits[0]), (tp2,hits[1]), (tp3,hits[2])]):
        yy = y + i*90
        icon = "✅" if hit else "⏰"
        status = "HIT" if hit else "PENDING"
        col = (0,255,100) if hit else (201,169,55)
        draw.text((200, yy), f"{icon} TP{i+1} {tp:.0f}", fill=col, font=f_big, anchor="lm")
        draw.text((W-250, yy), status, fill=col, font=f_mid, anchor="lm")

    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio, hits

@bot.message_handler(commands=['start','check','signal'])
def handle(m):
    price = get_price()
    side = "SELL"
    rsi = 78
    entry = price
    sl = entry + 12
    tp1 = entry - 10
    tp2 = entry - 20
    tp3 = entry - 35

    signal = {"entry":entry, "sl":sl, "tp1":tp1, "tp2":tp2, "tp3":tp3, "side":side, "rsi":rsi, "chat_id":m.chat.id}
    save_signal(signal)

    img, hits = make_image_with_checks(price, signal)
    bot.send_message(m.chat.id, f"🔥 НОВЫЙ СИГНАЛ! {side} {entry:.2f}\nTP1 {tp1:.0f} TP2 {tp2:.0f} TP3 {tp3:.0f}\nБот будет сам ставить ✅ когда пройдет!")
    bot.send_photo(m.chat.id, img)

@bot.message_handler(commands=['status'])
def status(m):
    sig = load_signal()
    if not sig:
        bot.send_message(m.chat.id, "Нет активного сигнала. Напиши /check")
        return
    price = get_price()
    img, hits = make_image_with_checks(price, sig)
    txt = f"📊 Цена сейчас {price:.2f}\n"
    txt += f"{'✅' if hits[0] else '⏰'} TP1 {sig['tp1']:.0f}\n"
    txt += f"{'✅' if hits[1] else '⏰'} TP2 {sig['tp2']:.0f}\n"
    txt += f"{'✅' if hits[2] else '⏰'} TP3 {sig['tp3']:.0f}\n"
    if all(hits): txt += "\n🎉 ВСЕ ТР TP ВЗЯТЫ!!!"
    bot.send_message(m.chat.id, txt)
    bot.send_photo(m.chat.id, img)

def auto_checker():
    while True:
        time.sleep(60)
        sig = load_signal()
        if not sig: continue
        price = get_price()
        img, hits = make_image_with_checks(price, sig)
        # Если только что взяло новый TP - отправляем апдейт
        # Сохраняем hits чтобы не спамить
        try:
            last_hits = sig.get('last_hits', [False,False,False])
            if hits != last_hits:
               
