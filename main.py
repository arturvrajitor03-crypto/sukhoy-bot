import os
import io
import requests
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sukhoy-bot.onrender.com")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_data():
    try:
        url = "https://data-api.binance.vision/api/v3/klines"
        params = {"symbol": "PAXGUSDT", "interval": "15m", "limit": 200}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if not data or isinstance(data, dict):
            return None
        df = pd.DataFrame(data, columns=[
            "time","Open","High","Low","Close","Volume",
            "close_time","qav","trades","tb_base","tb_quote","ignore"
        ])
        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = df[col].astype(float)
        return df
    except Exception as e:
        print(f"Data error: {e}")
        return None

def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def make_chart(df, ema_series, direction, entry, stop, tp1, tp2, tp3, price, rsi, ema50, strength):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), (12, 12, 14))
    draw = ImageDraw.Draw(img)

    # --- Шрифты ---
    def font(size, bold=True):
        try:
            name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
            return ImageFont.truetype(name, size)
        except:
            return ImageFont.load_default()

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

    # --- Золотая рамка внешняя ---
    for i in range(10):
        draw.rectangle([28+i, 280+i, W-28-i, H-110-i], outline=GOLD, width=1)
    # Тонкая внутренняя
    draw.rectangle([48, 300, W-48, H-130], outline=GOLD_DARK, width=2)
    # Белый центр
    draw.rectangle([85, 335, W-85, H-165], fill=WHITE)

    # --- Верх ---
    draw.text((W//2, 110), "👑  СУХОЙ  •  XAUUSD  👑", fill=GOLD, font=f_top, anchor="mm")
    draw.text((85, 210), "СУХОЙ", fill=GOLD, font=f_sukhoy, anchor="la")

    # Цена
