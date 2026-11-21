import os
import random
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

TOKEN = os.environ.get("BOT_TOKEN") or "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
print(f"TOKEN exists: {bool(os.environ.get('BOT_TOKEN'))}", flush=True)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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

def font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# ===== ГЛАВНАЯ КАРТИНКА - ТЕПЕРЬ С СИЛОЙ =====
def make_signal_from_template(direction, price, sl, tp1, tp2, tp3, sila=70):
    try:
        img = Image.open("template.jpg").convert("RGB")
    except Exception as e:
        print(f"template fail: {e}", flush=True)
        return None
    W, H = img.size
    draw = ImageDraw.Draw(img)
    if direction == "BUY":
        col = (0, 170, 80); arrow = "▲  BUY"
    elif direction == "SELL":
        col = (220, 30, 30); arrow = "▼  SELL"
    else:
        col = (180, 150, 40); arrow = "⏳  WAIT"
    x0, x1 = int(W*0.08), int(W*0.92)
    y0, y1 = int(H*0.60), int(H*0.96)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(255, 255, 255))
    draw.rounded_rectangle([x0+8, y0+8, x1-8, y1-8], radius=25, outline=(212, 175, 55), width=3)
    cx = W // 2
    f_dir = font(int(W*0.09))
    f_line = font(int(W*0.055))
    f_sila = font(int(W*0.05))
    f_small = font(int(W*0.035), bold=False)
    # Стрелка
    draw.text((cx, y0 + int(H*0.03)), arrow, font=f_dir, fill=col, anchor="mm")
    # СИЛА - сразу под стрелкой, золотым
    draw.text((cx, y0 + int(H*0.075)), f"Сила: {sila}%", font=f_sila, fill=(180, 140, 20), anchor="mm")
    y = y0 + int(H*0.125)
    step = int(H*0.041)
    draw.text((cx, y), f"Вход: {price:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step), f"SL: {sl:.2f}", font=f_line, fill=(180, 30, 30), anchor="mm")
    draw.text((cx, y+step*2), f"TP1: {tp1:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*3), f"TP2: {tp2:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*4), f"TP3: {tp3:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y1 - int(H*0.02)), "СУХОЙ - XAUUSD - Risk 1% - RR 1:2", font=f_small, fill=(120, 120, 120), anchor="mm")
    buf = BytesIO(); img.save(buf, format="JPEG", quality=92); buf.seek(0)
    return buf

def get_check_data():
    import yfinance as yf
    df = yf.download("GC=F", period="1d", interval="15m", progress=False, auto_adjust=False)
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    closes = df["Close"].values.flatten()
    s = pd.Series(closes)
    price = float(closes[-1])
    ema50 = round(float(s.ewm(span=50).mean().iloc[-1]), 2)
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = float(100 - (100 / (1 + rs.iloc[-1])))
    high = float(s.max()); low = float(s.min())
    fib618 = round(high - (high - low) * 0.618, 2)
    fib382 = round(high - (high - low) * 0.382, 2)
    return price, ema50, rsi, fib618, fib382, df

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
    n = len(closes)
    for i in range(n):
        c = "green" if closes[i] >= opens[i] else "red"
        ax.plot([i, i], [lows[i], highs[i]], color=c, linewidth=1)
        ax.plot([i-0.3, i+0.3], [opens[i], opens[i]], color=c, linewidth=2)
        ax.plot([i-0.3, i+0.3], [closes[i], closes[i]], color=c, linewidth=2)
    s = pd.Series(closes)
    ema = s.ewm(span=50).mean().values
    ax.plot(ema, color="blue", linewidth=1.2, label="EMA50")
    ax.axhline(fib618, color="orange", linestyle="--", linewidth=1, label="Fib 0.618")
    ax.axhline(fib382, color="purple", linestyle="--", linewidth=1, label="Fib 0.382")
    ax.set_title("SUKHOY - XAUUSD - 15m", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    return buf

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "👑 <b>СУХОЙ • XAUUSD</b>\n\nНапиши /check - живой сигнал с графиком\nИли выбери раздел:", parse_mode="HTML", reply_markup=kb_main())

@bot.message_handler(commands=["check"])
def check(m):
    # ТЕКСТА БОЛЬШЕ НЕТ - только картинки
    try:
        price, ema50, rsi, fib618, fib382, df = get_check_data()
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка данных: {e}")
        return
    if price > ema50 and rsi < 65:
        signal, sila = "BUY", 80
        sl = round(price - 18, 2); tp1 = round(price + 10, 2); tp2 = round(price + 20, 2); tp3 = round(price + 30, 2)
    elif price < ema50 and rsi > 35:
        signal, sila = "SELL", 65
        sl = round(price + 18, 2); tp1 = round(price - 10, 2); tp2 = round(price - 20, 2); tp3 = round(price - 30, 2)
    else:
        signal, sila = "WAIT", 50
        sl = round(price - 18, 2); tp1 = round(price + 10, 2); tp2 = round(price + 20, 2); tp3 = round(price + 30, 2)

    # 1. График - БЕЗ ТЕКСТА
    img_chart = make_chart(df, ema50, fib618, fib382)
    bot.send_photo(m.chat.id, img_chart)
