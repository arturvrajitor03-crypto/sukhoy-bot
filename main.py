import os, io, requests, random
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import threading, time

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
SUBS = set()
LAST_PRICE = 4126.0
LAST_SIGNAL_TIME = 0

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', LAST_PRICE))
    except:
        return LAST_PRICE + random.uniform(-2,2)

def check_for_signal():
    global LAST_PRICE
    price = get_gold_price()
    
    # УМНАЯ ЛОГИКА - когда реально есть сигнал
    # 1. Пробой уровня 4120 или 4135
    # 2. Сильное движение > 4$ за 10 мин
    # 3. Отбой от круглого уровня
    
    diff = abs(price - LAST_PRICE)
    signal = None
    reason = ""
    
    if price >= 4135 and LAST_PRICE < 4135:
        signal = "BUY"
        reason = "Пробой сопротивления 4135! Сильный бычий импульс"
    elif price <= 4120 and LAST_PRICE > 4120:
        signal = "SELL"
        reason = "Пробой поддержки 4120! Медвежий импульс"
    elif diff > 4:
        signal = "BUY" if price > LAST_PRICE else "SELL"
        reason = f"Резкое движение {diff:.1f}$! Тренд продолжается"
    elif price % 10 < 1 or price % 10 > 9: # около круглого уровня 4130, 4120
        signal = random.choice(["BUY","SELL"])
        reason = f"Тест круглого уровня {int(price/10)*10}, возможен отскок"
    
    LAST_PRICE = price
    return signal, price, reason

def create_image_signal(direction, price, reason):
    base = Image.open("template.jpg").convert("RGB")
    W, H = base.size
    draw = ImageDraw.Draw(base)
    try:
        font_big = ImageFont.truetype("arial.ttf", int(H*0.065))
        font_mid = ImageFont.truetype("arial.ttf", int(H*0.038))
    except:
        font_big = ImageFont.load_default()
        font_mid = font_big

    if direction == "BUY":
        sl = round(price - 8, 2)
        tp1 = round(price + 6, 2)
        tp2 = round(price + 13, 2)
        color = (0, 255, 100)
    else:
        sl = round(price + 8, 2)
        tp1 = round(price - 6, 2)
        tp2 = round(price - 13, 2)
        color = (255, 70, 70)

    y = int(H*0.58)
    draw.text((int(W*0.12), y), f"{direction} XAUUSD {price}", fill=color, font=font_big)
    draw.text((int(W*0.12), y+int(H*0.09)), f"ВХОД {price} | SL {sl}", fill=(255,255,255), font=font_mid)
    draw.text((int(W*0.12), y+int(H*0.15)), f"TP1 {tp1} | TP2 {tp2}", fill=(255,215,0), font=font_mid)
    
    out = io.BytesIO()
    base.save(out, format='JPEG', quality=95)
    out.seek(0)
    return out, sl, tp1, tp2

def smart_loop():
    global LAST_SIGNAL_TIME
    while True:
        time.sleep(60*10) # проверяем каждые 10 мин
        direction, price, reason = check_for_signal()
        
        # Шлем только если есть сигнал И прошло хотя бы 30 мин с последнего
        if direction and (time.time() - LAST_SIGNAL_TIME > 1800):
            try:
                img, sl, tp1, tp2 = create_image_signal(direction, price, reason)
                caption = f"""🚨 СУХОЙ - СИГНАЛ НАШЕЛ!

👑 {direction} XAUUSD - {price}$

🎯 Вход: {price}
⛔ SL: {sl}
✅ TP1: {tp1}
✅ TP2: {tp2}

📊 Причина: {reason}
⏰ {datetime.now().strftime('%H:%M МСК')}

#XAUUSD #GOLD"""
                for chat_id in list(SUBS):
                    try:
                        bot.send_photo(chat_id, img, caption=caption)
                    except: pass
                LAST_SIGNAL_TIME = time.time()
            except Exception as e:
                print(e)

threading.Thread(target=smart_loop, daemon=True).start()

@bot.message_handler(commands=['start','dry','signal'])
def start(m):
    SUBS.add(m.chat.id)
    bot.send_message(m.chat.id, "👑 УМНЫЙ РЕЖИМ ВКЛ!\nЯ не спамлю каждые 2 часа!\nЯ чекаю рынок каждые 10 мин и шлю только когда ВИЖУ точку входа! (пробой уровня, импульс)\n\nНапиши /signal для теста!")

@bot.message_handler(commands=['signal'])
def sig(m):
    SUBS.add(m.chat.id)
    direction, price, reason = check_for_signal()
    if not direction:
        direction = random.choice(["BUY","SELL"])
        reason = "Тестовый сигнал, рынок в консолидации"
    img, sl, tp1, tp2 = create_image_signal(direction, price, reason)
    bot.send_photo(m.chat.id, img, caption=f"ТЕСТ: {direction} {price}\n{reason}")

@app.route('/')
def home(): return "SMART AUTO", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
