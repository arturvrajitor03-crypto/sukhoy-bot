import os
import random
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= КНОПКИ =================
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

# ================= КАРТИНКА СУХОЙ GOLD (только для кнопки Сигнал) =================
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
    f_top = font(48, True); f_sukhoy = font(110, True); f_arrow = font(260, True)
    f_dir = font(72, True); f_line = font(62, True); f_small = font(38, True); f_price = font(52, True)
    GOLD = (212, 175, 55); WHITE = (245, 245, 245); BLACK = (0, 0, 0)
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
    buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0); return buf

# ================= ДАННЫЕ ДЛЯ /check =================
def get_check_data():
    import yfinance as yf
    df = yf.download("GC=F", period="1d", interval="15m", progress=False, auto_adjust=False)
    # yfinance иногда возвращает MultiIndex колонки - чиним
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    closes = df["Close"].values.flatten()
    s = pd.Series(closes)
    price = float(closes[-1])
    ema50 = float(s.ewm(span=50).mean().iloc[-1])
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = float(100 - (100 / (1 + rs.iloc[-1])))
    high = float(s.max()); low = float(s.min())
    fib618 = round(high - (high - low) * 0.618, 2)
    fib382 = round(high - (high - low) * 0.382, 2)
    return price, ema50, rsi, fib618, fib382, df

# ================= ГРАФИК ДЛЯ /check - свечи + EMA + Fib =================
def make_chart(df, ema50, fib618, fib382):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    closes = df["Close"].values.flatten()
    opens = df["Open"].values.flatten()
    highs = df["High"].values.flatten()
    lows = df["Low"].values.flatten()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # Свечи
    for i in range(len(closes)):
        col = "green" if closes[i] >= opens[i] else "red"
        ax.plot([i, i], [lows[i], highs[i]], color=col, linewidth=1)
        ax.plot([i - 0.3, i + 0.3], [opens[i], opens[i]], color=col, linewidth=2)
        ax.plot([i - 0.3, i + 0.3], [closes[i], closes[i]], color=col, linewidth=2)

    # EMA50
    s = pd.Series(closes)
    ema_line = s.ewm(span=50).mean().values
    ax.plot(ema_line, color="blue", linewidth=1.2, label=f"EMA50 {ema50:.2f}")

    # Fib
    ax.axhline(fib618, color="orange", linestyle="--", linewidth=1, label=f"Fib 0.618 {fib618:.2f}")
    ax.axhline(fib382, color="purple", linestyle="--", linewidth=1, label=f"Fib 0.382 {fib382:.2f}")

    ax.set_title("СУХОЙ - XAUUSD - 15m", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    return buf

# ================= КОМАНДЫ =================
@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "👑 <b>СУХОЙ • XAUUSD</b>\n\nНапиши /check - живой сигнал с графиком\nИли выбери раздел:", parse_mode="HTML", reply_markup=kb_main())

@bot.message_handler(commands=["check"])
def check(m):
    bot.send_message(m.chat.id, "*Сухой*\n⌛ Считаю EMA + RSI + Fib + рисую график...", parse_mode="Markdown")
    try:
        price, ema50, rsi, fib618, fib382, df = get_check_data()
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка данных: {e}\nПопробуй ещё раз через минуту.")
        return

    if price > ema50 and rsi < 65:
        signal, sila = "BUY", 70
        sl = round(price - 18, 2); tp1 = round(price + 10, 2); tp2 = round(price + 20, 2); tp3 = round(price + 30, 2)
        reason = f"Цена выше EMA50, RSI {int(rsi)} - есть импульс вверх"
        emoji = "🟢"
    elif price < ema50 and rsi > 35:
        signal, sila = "SELL", 65
        sl = round(price + 18, 2); tp1 = round(price - 10, 2); tp2 = round(price - 20, 2); tp3 = round(price - 30, 2)
        reason = f"Цена ниже EMA50, RSI {int(rsi)} - давление вниз"
        emoji = "🔴"
    else:
        signal, sila = "WAIT", 50
        sl = round(price - 18, 2); tp1 = round(price + 10, 2); tp2 = round(price + 20, 2); tp3 = round(price + 30, 2)
        reason = f"Нет чёткого сигнала: Цена {price} / EMA50 {ema50} / RSI {int(rsi)} - лучше пропустить"
        emoji = "⏳"

    img = make_chart(df, ema50, fib618, fib382)
    text = (
        f"👑 СУХОЙ - XAUUSD - {emoji} {signal}\n\n"
        f"💰 Цена: {price}\n"
        f"📊 RSI: {int(rsi)} | EMA50: {ema50} | Сила: {sila}%\n"
        f"📉 {reason}\n"
        f"Fib 0.618: {fib618} | Fib 0.382: {fib382}\n\n"
        f"Вход: {price}\n"
        f"СТОП: {sl}\n"
        f"ЦЕЛЬ 1: {tp1}\n"
        f"ЦЕЛЬ 2: {tp2}\n"
        f"ЦЕЛЬ 3: {tp3}"
    )
    bot.send_photo(m.chat.id, img, caption=text)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "back":
        bot.edit_message_text("👑 <b>СУХОЙ • XAUUSD</b>\n\nВыбери раздел:", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_main())
    elif c.data == "signal":
        price = round(random.uniform(3500, 3530), 2)
        is_buy = random.choice([True, False])
        direction = "BUY" if is_buy else "SELL"
        tp = round(price + 20 if is_buy else price - 20, 2)
        sl = round(price - 10 if is_buy else price + 10, 2)
        img = make_image(direction, price, tp, sl)
        bot.send_photo(c.message.chat.id, img, caption=f"🔥 <b>{direction} XAUUSD</b>\n\nEntry: {price}\nTP: {tp}\nSL: {sl}", parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "analytics":
        bot.edit_message_text("📈 <b>Аналитика</b>\n\nЗолото держится выше 2650. Ключевой уровень - 2665. Пробой вверх - дальше к 2680.", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "news":
        bot.edit_message_text("📰 <b>Новости</b>\n\n• Доллар под давлением\n• Золото - защитный актив\n• Сегодня: данные по инфляции США в 15:30", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "vip":
        bot.edit_message_text("💎 <b>VIP</b>\n\n• Сигналы раньше всех\n• Точные TP/SL\n• Личная поддержка\n\nПиши: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "help":
        bot.edit_message_text("❓ <b>Помощь</b>\n\nНажми /check - живой сигнал с графиком.\nВопросы: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    bot.answer_callback_query(c.id)

# ================= WEBHOOK =================
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
