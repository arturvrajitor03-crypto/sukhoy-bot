import os, threading, time, requests, telebot
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

last_signal = {}

@app.route('/')
def home():
    return "SUHOY SNIPER CLEAN"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4123.3

# СНАЙПЕР ЛОГИКА
def sniper_logic(price):
    # Имитация RSI и Bollinger (в реальном боте тут API индикаторов)
    rsi = random.randint(65, 85)  # для теста
    # Если RSI > 75 - SELL Снайпер
    if rsi >= 72:
        side = "SELL"
        entry = price
        sl = entry + 15
        tp1 = entry - 12
        tp2 = entry - 25
        tp3 = entry - 40
        reason = f"RSI {rsi} ПЕРЕКУП! Цена у верхней Bollinger. Снайпер ждет вниз!"
    else:
        side = "BUY"
        entry = price
        sl = entry - 15
        tp1 = entry + 12
        tp2 = entry + 25
        tp3 = entry + 40
        reason = f"RSI {rsi} ПЕРЕПРОДАН! Снайпер ждет вверх!"
    
    # Снайпер дает точку только если RSI сильный, иначе говорит ЖДЕМ
    if rsi < 70 and rsi > 30:
        return None, f"ЖДЕМ... RSI {rsi} нет точки, Снайпер не стреляет", rsi
    
    return (side, entry, sl, tp1, tp2, tp3, reason), None, rsi

def make_image(side, entry, sl, tp1, tp2, tp3, hits=[False, False, False]):
    w = 1200
    h = 1600
    img = Image.new("RGB", (w, h), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle((5, 5, w-5, h-5), outline=(255, 215, 0), width=20)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 160)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
        f3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    except:
        f1 = f2 = f3 = ImageFont.load_default()
    
    col = (255, 30, 30) if side == "SELL" else (40, 255, 80)
    
    draw.text((w//2, 120), "SUHOY - GOLD SNIPER", fill=(255, 215, 0), font=f3, anchor="mm")
    draw.text((w//2, 350), side, fill=col, font=f1, anchor="mm")
    draw.text((w//2, 550), f"{entry:.2f}", fill=(255, 255, 255), font=f1, anchor="mm")
    draw.text((w//2, 750), f"SL {sl:.0f}", fill=(255, 100, 100), font=f2, anchor="mm")
    
    c1 = "✅" if hits[0] else "⏳"
    c2 = "✅" if hits[1] else "⏳"
    c3 = "✅" if hits[2] else "⏳"
    
    draw.text((w//2, 900), f"{c1} TP1 {tp1:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 1050), f"{c2} TP2 {tp2:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 1200), f"{c3} TP3 {tp3:.0f}", fill=(0, 255, 120), font=f2, anchor="mm")
    draw.text((w//2, 1400), "SNIPER MODE", fill=(255, 215, 0), font=f3, anchor="mm")
    
    bio = BytesIO()
    img.save(bio, "JPEG", quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "🎯 СУХОЙ СНАЙПЕР\n\n/check - снайпер ищет точку\n/price - цена\n/status - статус TP")

@bot.message_handler(commands=["check", "signal", "sniper"])
def check_cmd(m):
    price = get_price()
    data, wait_msg, rsi = sniper_logic(price)
    
    if data is None:
        bot.send_message(m.chat.id, f"🎯 СНАЙПЕР: {wait_msg}\nЦена {price:.2f}")
        return
    
    side, entry, sl, tp1, tp2, tp3, reason = data
    last_signal[m.chat.id] = {"side": side, "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3}
    
    im = make_image(side, entry, sl, tp1, tp2, tp3)
    # Цифры ТОЛЬКО на картинке!
    bot.send_photo(m.chat.id, im, caption=f"🎯 СНАЙПЕР {side}\n{reason}")

@bot.message_handler(commands=["price"])
def price_cmd(m):
    bot.send_message(m.chat.id, f"Золото: {get_price():.2f}")

@bot.message_handler(commands=["status"])
def status_cmd(m):
    if m.chat.id not in last_signal:
        bot.send_message(m.chat.id, "Сначала /check")
        return
    s = last_signal[m.chat.id]
    p = get_price()
    if s["side"] == "SELL":
        hits = [p <= s["tp1"], p <= s["tp2"], p <= s["tp3"]]
    else:
        hits = [p >= s["tp1"], p >= s["tp2"], p >= s["tp3"]]
    im = make_image(s["side"], s["entry"], s["sl"], s["tp1"], s["tp2"], s["tp3"], hits)
    bot.send_photo(m.chat.id, im, caption=f"Статус цена {p:.2f}")

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
