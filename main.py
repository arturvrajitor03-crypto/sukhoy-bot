import os, io, requests, random, threading, time
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

chat_ids = set()
last_prices = []
last_signal = 0

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
    return bio

def auto_checker():
    global last_prices, last_signal
    time.sleep(30)
    while True:
        try:
            price = get_price()
            last_prices.append(price)
            if len(last_prices) > 20:
                last_prices.pop(0)
            
            if len(last_prices) >= 10:
                avg = sum(last_prices[:-1]) / (len(last_prices)-1)
                diff = price - avg
                
                signal = None
                if diff < -3.5:
                    signal = "BUY"
                elif diff > 3.5:
                    signal = "SELL"
                
                if signal and (time.time() - last_signal > 1200) and chat_ids:
                    img = make_signal(price, signal)
                    for cid in list(chat_ids):
                        try:
                            bot.send_photo(cid, img, caption=f"VHOd {signal} {price}")
                        except:
                            pass
                    last_signal = time.time()
            
            time.sleep(120)
        except:
            time.sleep(60)

try:
    threading.Thread(target=auto_checker, daemon=True).start()
except:
    pass

@bot.message_handler(commands=['start'])
def s(m):
    chat_ids.add(m.chat.id)
    bot.send_message(m.chat.id, "Auto vhod vkluchen! Budu slat kogda est tochka BUY/SELL", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['signal','buy','sell','dry','remove'])
def cmd(m):
    chat_ids.add(m.chat.id)
    price = get_price()
    d = "BUY"
    if m.text:
        if "sell" in m.text.lower():
            d = "SELL"
        elif "buy" in m.text.lower():
            d = "BUY"
        else:
            d = random.choice(["BUY", "SELL"])
    img = make_signal(price, d)
    bot.send_photo(m.chat.id, img)

@app.route('/')
def h():
    return "ENTRY BOT LIVE",200

@app.route('/webhook', methods=['POST'])
def wh():
    u = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([u])
    return 'ok',200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
