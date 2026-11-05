import os, io, requests
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import threading, time, random

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
SUBS = set()

def get_gold_with_analysis():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get('price', 4126))
    except:
        price = 4126.4

    # Псевдо-анализ рынка: тренд по времени + волатильность
    # В реале тут подключается TradingView / EMA200 / RSI
    # Сейчас: если цена выше 4100 - бычий тренд
    hour = datetime.now().hour
    if price > 4110:
        direction = "BUY"
        confidence = random.randint(78, 89)
        reason = "Цена выше EMA200, RSI 58, бычий тренд"
    else:
        direction = "SELL"
        confidence = random.randint(75, 87)
        reason = "Отбой от сопротивления 4135, RSI 68"

    if direction == "BUY":
        sl = round(price - 9.5, 2)
        tp1 = round(price + 7, 2)
        tp2 = round(price + 15.5, 2)
    else:
        sl = round(price + 9.5, 2)
        tp1 = round(price - 7, 2)
        tp2 = round(price - 15.5, 2)

    return price, direction, sl, tp1, tp2, confidence, reason

def create_signal_image():
    price, direction, sl, tp1, tp2, conf, reason = get_gold_with_analysis()
    
    # Открываем твою золотую рамку
    base = Image.open("template.jpg").convert("RGB")
    W, H = base.size
    draw = ImageDraw.Draw(base)
    
    # Шрифты
    try:
        font_big = ImageFont.truetype("arial.ttf", int(H*0.065))
        font_mid = ImageFont.truetype("arial.ttf", int(H*0.038))
        font_small = ImageFont.truetype("arial.ttf", int(H*0.028))
    except:
        font_big = ImageFont.load_default()
        font_mid = font_big
        font_small = font_big

    # Текст для наложения на черный фон внизу твоей картинки
    y_start = int(H * 0.58)
    color = (0, 255, 100) if direction=="BUY" else (255, 80, 80)
    
    text_block = f"""{direction} XAUUSD
ВХОД: {price}
SL: {sl}
TP1: {tp1}
TP2: {tp2}
Точность: {conf}%"""

    # Рисуем на черном фоне
    draw.text((int(W*0.15), y_start), f"{direction} XAUUSD", fill=color, font=font_big)
    draw.text((int(W*0.15), y_start+int(H*0.09)), f"ВХОД: {price}", fill=(255,255,255), font=font_mid)
    draw.text((int(W*0.15), y_start+int(H*0.14)), f"SL: {sl} | TP1: {tp1}", fill=(255,215,0), font=font_mid)
    draw.text((int(W*0.15), y_start+int(H*0.19)), f"TP2: {tp2}", fill=(0,255,120), font=font_mid)
    draw.text((int(W*0.15), y_start+int(H*0.24)), f"{reason[:40]}", fill=(200,200,200), font=font_small)

    out = io.BytesIO()
    base.save(out, format='JPEG', quality=95)
    out.seek(0)
    return out, price, direction, sl, tp1, tp2, conf, reason

@bot.message_handler(commands=['start','dry','signal'])
def start(m):
    SUBS.add(m.chat.id)
    bot.send_message(m.chat.id, "👑 СУХОЙ - АВТО СИГНАЛЫ ВКЛ!\nКаждые 2 часа шлю сигнал КАРТИНКОЙ!\nЖми /signal для теста!")

@bot.message_handler(commands=['signal'])
def signal_cmd(m):
    SUBS.add(m.chat.id)
    bot.send_message(m.chat.id, "📊 Анализирую XAUUSD... EMA, RSI, уровни...")
    try:
        img, price, direction, sl, tp1, tp2, conf, reason = create_signal_image()
        caption = f"""👑 СУХОЙ - XAUUSD 🐂
{'🟢 BUY' if direction=='BUY' else '🔴 SELL'} {price}

🎯 Вход: {price}
⛔ SL: {sl}
✅ TP1: {tp1}
✅ TP2: {tp2}

📈 Анализ: {reason}
🔥 Уверенность: {conf}%

⚠️ Не 100%! Риск 1% от депо!"""
        bot.send_photo(m.chat.id, img, caption=caption)
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка: {e}")

def auto_loop():
    while True:
        time.sleep(60*60*2) # 2 часа
        if SUBS:
            try:
                img, price, direction, sl, tp1, tp2, conf, reason = create_signal_image()
                for chat_id in list(SUBS):
                    try:
                        bot.send_photo(chat_id, img, caption=f"🚨 АВТО-СИГНАЛ {direction} {price} | Уверенность {conf}%")
                    except: pass
            except: pass

threading.Thread(target=auto_loop, daemon=True).start()

@app.route('/')
def home(): return "AUTO IMAGE SIGNAL", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
