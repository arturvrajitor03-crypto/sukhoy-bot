import os
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN") or "123456:ABC"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            return ImageFont.load_default()

def pic(direct, price, sl, tp1, tp2, tp3, sila):
    if os.path.exists("template.jpg"):
        img = Image.open("template.jpg").convert("RGB")
    else:
        img = Image.new("RGB", (800, 1200), (20, 20, 20))

    W, H = img.size
    draw = ImageDraw.Draw(img)

    if direct == "BUY":
        col = (0, 170, 80)
        arr = "BUY"
    elif direct == "SELL":
        col = (220, 30, 30)
        arr = "SELL"
    else:
        col = (180, 150, 40)
        arr = "WAIT"

    x0 = int(W * 0.08)
    x1 = int(W * 0.92)
    y0 = int(H * 0.60)
    y1 = int(H * 0.96)

    draw.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(255, 255, 255))
    draw.rounded_rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], radius=25, outline=(212, 175, 55), width=3)

    cx = W // 2
    f_big = get_font(int(W * 0.09))
    f_mid = get_font(int(W * 0.055))
    f_small = get_font(int(W * 0.05))

    draw.text((cx, y0 + int(H * 0.03)), arr, font=f_big, fill=col, anchor="mm")
    draw.text((cx, y0 + int(H * 0.075)), "Sila: " + str(sila) + "%", font=f_small, fill=(180, 140, 20), anchor="mm")

    y = y0 + int(H * 0.125)
    st = int(H * 0.041)

    draw.text((cx, y), "Vhod: " + str(round(price, 2)), font=f_mid, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y + st), "SL: " + str(round(sl, 2)), font=f_mid, fill=(180, 30, 30), anchor="mm")
    draw.text((cx, y + st * 2), "TP1: " + str(round(tp1, 2)), font=f_mid, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y + st * 3), "TP2: " + str(round(tp2, 2)), font=f_mid, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y + st * 4), "TP3: " + str(round(tp3, 2)), font=f_mid, fill=(0, 0, 0), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf

def get_data():
    import yfinance as yf

    d15 = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=False)
    if hasattr(d15.columns, "nlevels") and d15.columns.nlevels > 1:
        d15.columns = d15.columns.get_level_values(0)
    d15 = d15.dropna()

    d1h = yf.download("GC=F", period="1mo", interval="1h", progress=False, auto_adjust=False)
    if hasattr(d1h.columns, "nlevels") and d1h.columns.nlevels > 1:
        d1h.columns = d1h.columns.get_level_values(0)
    d1h = d1h.dropna()

    s = pd.Series(d15["Close"].values.flatten())
    s1h = pd.Series(d1h["Close"].values.flatten())

    price = float(s.iloc[-1])
    ema50 = float(s.ewm(span=50).mean().iloc[-1])
    e200 = float(s1h.ewm(span=200).mean().iloc[-1])
    trend = "UP" if price > e200 else "DOWN"

    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = float(100 - (100 / (1 + gain / loss.iloc[-1])))

    e12 = s.ewm(span=12).mean()
    e26 = s.ewm(span=26).mean()
    macd = e12 - e26
    ms = macd.ewm(span=9).mean()

    ma20 = s.rolling(20).mean()
    sd = s.rolling(20).std()
    bbu = float(ma20.iloc[-1] + 2 * sd.iloc[-1])
    bbl = float(ma20.iloc[-1] - 2 * sd.iloc[-1])

    hi = d15["High"].values.flatten()
    lo = d15["Low"].values.flatten()
    cl = d15["Close"].values.flatten()
    tr1 = hi[1:] - lo[1:]
    tr2 = abs(hi[1:] - cl[:-1])
    tr3 = abs(lo[1:] - cl[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr = float(pd.Series(tr).rolling(14).mean().iloc[-1])
    atr = max(5, min(20, atr))

    h5 = float(s.max())
    l5 = float(s.min())
    f618 = round(h5 - (h5 - l5) * 0.618, 2)
    f382 = round(h5 - (h5 - l5) * 0.382, 2)

    return {
        "price": price,
        "ema50": ema50,
        "trend": trend,
        "rsi": rsi,
        "macd": float(macd.iloc[-1]),
        "ms": float(ms.iloc[-1]),
        "bbu": bbu,
        "bbl": bbl,
        "atr": atr,
        "f618": f618,
        "f382": f382,
        "df": d15
    }

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
        return "BUY", min(95, 65 + buy * 4), round(p - a * 1.5, 2), round(p + a * 1.2, 2), round(p + a * 2.2, 2), round(p + a * 3.2, 2)
    if sell >= 5 and sell > buy + 1:
        return "SELL", min(95, 65 + sell * 4), round(p + a * 1.5, 2), round(p - a * 1.2, 2), round(p - a * 2.2, 2), round(p - a * 3.2, 2)

    return "WAIT", 45, round(p - a * 1.5, 2), round(p + a * 1.2, 2), round(p + a * 2.2, 2), round(p + a * 3.2, 2)

def chart(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cl = df["Close"].values.flatten()
    op = df["Open"].values.flatten()
    hi = df["High"].values.flatten()
    lo = df["Low"].values.flatten()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    for i in range(len(cl)):
        c = "green" if cl[i] >= op[i] else "red"
        ax.plot([i, i], [lo[i], hi[i]], color=c, linewidth=1)
        ax.plot([i - 0.3, i + 0.3], [op[i], op[i]], color=c, linewidth=2)
        ax.plot([i - 0.3, i + 0.3], [cl[i], cl[i]], color=c, linewidth=2)

    ema_line = pd.Series(cl).ewm(span=50).mean().values
    ax.plot(ema_line, color="blue", linewidth=1.2, label="EMA50")
    ax.set_title("SUKHOY - XAUUSD - PRO", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    return buf

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "SUKHOY XAUUSD PRO - Napishi /check")

@bot.message_handler(commands=["check"])
def check(m):
    bot.send_message(m.chat.id, "PRO analiz...")
    try:
        d = get_data()
        sig, sila, sl, tp1, tp2, tp3 = calc(d)
        price = d["price"]
    except Exception as e:
        bot.send_message(m.chat.id, "Oshibka: " + str(e))
        return
    bot.send_photo(m.chat.id, chart(d["df"]))
    im = pic(sig, price, sl, tp1, tp2, tp3, sila)
    if im:
        bot.send_photo(m.chat.id, im)

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    data = request.stream.read().decode("utf-8")
    upd = telebot.types.Update.de_json(data)
    bot.process_new_updates([upd])
    return "OK", 200

@app.route("/")
def index():
    return "Sukhoy Bot is alive!", 200

if __name__ == "__main__":
    print("=== STARTING ===", flush=True)
    try:
        if os.environ.get("BOT_TOKEN"):
            bot.remove_webhook()
            bot.set_webhook(url=APP_URL + "/" + TOKEN)
            print("Webhook set!", flush=True)
    except Exception as e:
        print("Webhook error: " + str(e), flush=True)
        traceback.print_exc()
    port = int(os.environ.get("PORT", 10000))
    print("Port " + str(port), flush=True)
    app.run(host="0.0.0.0", port=port)
