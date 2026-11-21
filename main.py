import os
import random
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Кнопки ---
def kb_main():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("📊 Сигнал", callback_data="signal"))
    m.add(telebot.types.InlineKeyboardButton("📈 Аналитика", callback_data="analytics"),
          telebot.types.InlineKeyboardButton("📰 Новости", callback_data="news"))
    m.add(telebot.types.InlineKeyboardButton("💎 VIP", callback_data="vip"),
          telebot.types.InlineKeyboardButton("❓ Помощь", callback_data="help"))
    return m

def kb_back():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return m

# --- Картинка ---
def font(size, bold=False):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

def make_image(direction, price, tp, sl):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (10, 10, 12))
    draw = ImageDraw.Draw(img)
    f_top = font(48, True)
    f_sukhoy = font(110, True)
    f_arrow = font(260, True)
    f_dir = font(72, True)
    f_line = font(62, True)
    f_small = font(38, True)
    f_price = font(52, True)
    GOLD = (212, 175, 55)
    GOLD_DARK = (180, 140, 40)
    WHITE = (245, 245, 245)
    BLACK = (0, 0, 0)

    for i in range(10):
        draw.rectangle([28+i, 280+i, W-28-i, H-28-i], outline=GOLD)
    draw.rectangle([48, 300, W-48, H-130], outline=GOLD, width=2)
    draw.rectangle([85, 335, W-85, H-165], fill=(255, 255, 255))

    draw.text((W//2, 110), "🔥  СУХОЙ  •  XAUUSD", font=f_top, fill=GOLD, anchor="mm")
    draw.text((85, 210), "СУХОЙ", font=f_sukhoy, fill=GOLD)
    draw.text((W-85, 210), "GOLD", font=f_sukhoy, fill=WHITE, anchor="ra")

    arrow = "▲" if direction == "BUY" else "▼"
    col = (0, 180, 90) if direction == "BUY" else (220, 50, 50)
    draw.text((W//2, 560), arrow, font=f_arrow, fill=col, anchor="mm")
    draw.text((W//2, 740), direction, font=f_dir, fill=col, anchor="mm")
    draw.text((W//2, 830), f"Entry: {price}", font=f_line, fill=BLACK, anchor="mm")
    draw.text((W//2, 910), f"TP: {tp}  |  SL: {sl}", font=f_line, fill=BLACK, anchor="mm")
    draw.text((W//2, 1010), "Risk 1%  •  RR 1:2", font=f_small, fill=(120,120,120), anchor="mm")
    draw.text((W//2, H-70), "t.me/sukhoy  •  @sukhoy_bot", font=f_price, fill=GOLD, anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- Хендлеры ---
@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "👑 <b>СУХОЙ • XAUUSD</b>\n\nВыбери раздел:", parse_mode="HTML", reply_markup=kb_main())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "back":
        bot.edit_message_text("👑 <b>СУХОЙ • XAUUSD</b>\n\nВыбери раздел:", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_main())
        return
    if c.data == "signal":
        price = round(random.uniform(2640, 2660), 2)
        is_buy = random.choice([True, False])
        direction = "BUY" if is_buy else "SELL"
        tp = round(price + 20 if is_buy else price - 20, 2)
        sl = round(price - 10 if is_buy else price + 10, 2)
        img = make_image(direction, price, tp, sl)
        bot.send_photo(c.message.chat.id, img, caption=f"🔥 <b>{direction} XAUUSD</b>\n\nEntry: {price}\nTP: {tp}\nSL: {sl}\n\nRisk 1% • RR 1:2", parse_mode="HTML", reply_markup=kb_back())
        bot.answer_callback_query(c.id)
        return
    if c.data == "analytics":
        bot.edit_message_text("📈 <b>Аналитика XAUUSD</b>\n\nЗолото держится выше 2650. Ключевой уровень - 2665. Пробой вверх - дальше к 2680.", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "news":
        bot.edit_message_text("📰 <b>Новости</b>\n\n• Доллар под давлением\n• Золото - защитный актив\n• Сегодня: данные по инфляции США в 15:30", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "vip":
        bot.edit_message_text("💎 <b>VIP</b>\n\n• Сигналы раньше всех\n• Точные TP/SL\n• Личная поддержка\n\nПиши: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "help":
        bot.edit_message_text("❓ <b>Помощь</b>\n\nНажми Сигнал - получишь картинку с входом.\nВопросы: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    bot.answer_callback_query(c.id)

# --- Webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def index():
    return "Sukhoy Bot is alive!", 200

if __name__ == "__main__":
    print("=== STARTING SUKHOY BOT ===", flush=True)
    print(f"TOKEN exists: {bool(TOKEN)}", flush=True)
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
        print("Webhook set!", flush=True)
    except Exception as e:
        print(f"Webhook error: {e}", flush=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
