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

# ================= ФУНКЦИИ ДЛЯ ШРИФТОВ =================
def font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# ================= КРАСИВАЯ КАРТИНКА НА ТВОЕМ ШАБЛОНЕ template.jpg =================
def make_signal_from_template(direction, price, sl, tp1, tp2, tp3):
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

    # Белая табличка внизу
    x0, x1 = int(W*0.08), int(W*0.92)
    y0, y1 = int(H*0.60), int(H*0.96)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(255, 255, 255))
    draw.rounded_rectangle([x0+8, y0+8, x1-8, y1-8], radius=25, outline=(212, 175, 55), width=3)

    cx = W // 2
    f_dir = font(int(W*0.09))
    f_line = font(int(W*0.058))
    f_small = font(int(W*0.035), bold=False)

    draw.text((cx, y0 + int(H*0.035)), arrow, font=f_dir, fill=col, anchor="mm")
    y = y0 + int(H*0.095)
    step = int(H*0.045)
    draw.text((cx, y), f"Вход: {price:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step), f"SL: {sl:.2f}", font=f_line, fill=(180, 30, 30), anchor="mm")
    draw.text((cx, y+step*2), f"TP1: {tp1:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*3), f"TP2: {tp2:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*4), f"TP3: {tp3:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y1 - int(H*0.025)), "СУХОЙ • XAUUSD • Risk 1% • RR 1:2", font=f_small, fill=(120, 120, 120), anchor="mm")

    buf = BytesIO(); img.save(buf, format="JPEG", quality=92); buf.seek(0)
    return buf

# ================= ДАННЫЕ ДЛЯ /check =================
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
    high = float(s.max());
