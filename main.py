import os
import traceback
from io import BytesIO
from flask import Flask
from flask import request
import telebot
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import pandas as pd
import numpy as np
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
U = os.environ.get("RENDER_EXTERNAL_URL")
U = U.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
def get_font(s):
    try:
        f = "DejaVuSans-Bold.ttf"
        r = ImageFont.truetype(f, s)
        return r
    except:
        try:
            f2 = "/usr/share/fonts/"
            f2 += "truetype/dejavu/"
            f2 += "DejaVuSans-Bold.ttf"
            r = ImageFont.truetype(f2, s)
            return r
        except:
            r = ImageFont.load_default()
            return r
def pic(d, p, sl, a, b, c, s):
    if os.path.exists("template.jpg"):
        img = Image.open("template.jpg")
        img = img.convert("RGB")
    else:
        sz = (800, 1200)
        img = Image.new("RGB", sz)
    W, H = img.size
    draw = ImageDraw.Draw(img)
    if d == "BUY":
        col = (0, 170, 80)
        arr = "BUY"
    elif d == "SELL":
        col = (220, 30, 30)
        arr = "SELL"
    else:
        col = (180, 150, 40)
        arr = "WAIT"
    x0 = int(W * 0.08)
    x1 = int(W * 0.92)
    y0 = int(H * 0.60)
    y1 = int(H * 0.96)
    box = [x0, y0, x1, y1]
    draw.rectangle(box, fill=(255, 255, 255))
    box2 = [x0 + 8, y0 + 8, x1 - 8, y1 - 8]
    draw.rectangle(box2, outline=(212, 175, 55))
    cx = W // 2
    f_big = get_font(int(W * 0.09))
    f_mid = get_font(int(W * 0.055))
    f_small = get_font(int(W * 0.05))
    y_big = y0 + int(H * 0.03)
    draw.text((cx, y_big), arr)
    y_sila = y0 + int(H * 0.075)
    t0 = "Sila: " + str(s) + "%"
    draw.text((cx, y_sila), t0)
    y = y0 + int(H * 0.125)
    st = int(H * 0.041)
    t1 = "Vhod: " + str(round(p, 2))
    draw.text((cx, y), t1)
    t2 = "SL: " + str(round(sl, 2))
    draw.text((cx, y + st), t2)
    t3 = "TP1: " + str(round(a, 2))
    draw.text((cx, y + st * 2), t3)
    t4 = "TP2: " + str(round(b, 2))
    draw.text((cx, y + st * 3), t4)
    t5 = "TP3: " + str(round(c, 2))
    draw.text((cx, y + st * 4), t5)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf
def get_data():
    import yfinance as yf
    t = "GC=F"
    d15 = yf.download(t, "5d", "15m")
    cc = d15.columns
    if cc.nlevels > 1:
        d15.columns = cc.get_level_values(0)
    d15 = d15.dropna()
    d1h = yf.download(t, "1mo", "1h")
    cc = d1h.columns
    if cc.nlevels > 1:
        d1h.columns = cc.get_level_values(0)
    d1h = d1h.dropna()
    s = pd.Series(d15["Close"].values)
    s = pd.Series(s.values.flatten())
    s1h = pd.Series(d1h["Close"].values)
    s1h = pd.Series(s1h.values.flatten())
    price = float(s.iloc[-1])
    e = s.ewm(span=50).mean()
    ema50 = float(e.iloc[-1])
    e2 = s1h.ewm(span=200).mean()
    e200 = float(e2.iloc[-1])
    if price > e200:
        trend = "UP"
    else:
        trend = "DOWN"
    delta = s.diff()
    g1 = delta > 0
    gain = delta.where(g1, 0)
    g2 = gain.rolling(14).mean()
    gain = g2
    l1 = delta < 0
    loss = -delta.where(l1, 0)
    l2 = loss.rolling(14).mean()
    loss = l2
    g = float(np.array(gain).flatten()[-1])
    l = float(np.array(loss).flatten()[-1])
    if l != 0:
        rsi = 100 - (100 / (1 + g / l))
        rsi = float(rsi)
    else:
        rsi = 50.0
    e12 = s.ewm(span=12).mean()
    e26 = s.ewm(span=26).mean()
    macd = e12 - e26
    ms = macd.ewm(span=9).mean()
    ma20 = s.rolling(20).mean()
    sd = s.rolling(20).std()
    b1 = ma20.iloc[-1]
    b2 = sd.iloc[-1]
    bbu = float(b1 + 2 * b2)
    bbl = float(b1 - 2 * b2)
    hi = d15["High"].values.flatten()
    lo = d15["Low"].values.flatten()
    cl = d15["Close"].values.flatten()
    tr1 = hi[1:] - lo[1:]
    tr2 = abs(hi[1:] - cl[:-1])
    tr3 = abs(lo[1:] - cl[:-1])
    tr = np.maximum(tr1, tr2)
    tr = np.maximum(tr, tr3)
    at = pd.Series(tr).rolling(14).mean()
    atr = float(at.iloc[-1])
    atr = max(5, min(20, atr))
    h5 = float(s.max())
    l5 = float(s.min())
    f618 = round(h5 - (h5 - l5) * 0.618, 2)
    f382 = round(h5 - (h5 - l5) * 0.382, 2)
    mc = float(np.array(macd).flatten()[-1])
    ms2 = float(np.array(ms).flatten()[-1])
    return {"price": price, "ema50": ema50, "trend": trend, "rsi": rsi, "macd": mc, "ms": ms2, "bbu": bbu, "bbl": bbl, "atr": atr, "f618": f618, "f382": f382, "df": d15}
def calc(d):
    p = d["price"]
    buy = 0
    sell = 0
    if d["trend"] == "UP":
        buy += 3
    else:
        sell += 3
    if p > d["ema50"]:
        buy += 1
    else:
        sell += 1
    if d["macd"] > d["ms"]:
        buy += 1
    else:
        sell += 1
    if 50 < d["rsi"] < 68:
        buy += 1
    elif 32 < d["rsi"] < 50:
        sell += 1
    if p <= d["bbl"] * 1.002:
        buy += 1
    elif p >= d["bbu"] * 0.998:
        sell += 1
    if abs(p - d["f618"]) < d["atr"]:
        buy += 1
    if abs(p - d["f382"]) < d["atr"]:
        sell += 1
    a = d["atr"]
    if buy >= 5 and buy > sell + 1:
        sl = round(p - a * 1.5, 2)
        t1 = round(p + a * 1.2, 2)
        t2 = round(p + a * 2.2, 2)
        t3 = round(p + a * 3.2, 2)
        sila = min(95, 65 + buy * 4)
        return "BUY", sila, sl, t1, t2, t3
    if sell >= 5 and sell > buy + 1:
        sl = round(p + a * 1.5, 2)
        t1 = round(p - a * 1.2, 2)
        t2 = round(p - a * 2.2, 2)
        t3 = round(p - a * 3.2, 2)
        sila = min(95, 65 + sell * 4)
        return "SELL", sila, sl, t1, t2, t3
    sl = round(p - a * 1.5, 2)
    t1 = round(p + a * 1.2, 2)
    t2 = round(p + a * 2.2, 2)
    t3 = round(p + a * 3.2, 2)
    return "WAIT", 45, sl, t1, t2, t3
def chart(df):
    df = df.tail(120)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
