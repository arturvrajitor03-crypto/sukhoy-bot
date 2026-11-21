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

TOKEN = os.environ.get(
"BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
APP_URL = os.environ.get(
"RENDER_EXTERNAL_URL",
"")
APP_URL = APP_URL.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_font(s):
    try:
        f = "DejaVuSans-Bold.ttf"
        return ImageFont.truetype(
        f, s)
    except:
        try:
            f2 = "/usr/share/fonts/"
            f2 += "truetype/dejavu/"
            f2 += "DejaVuSans-Bold.ttf"
            return ImageFont.truetype(
            f2, s)
        except:
            return ImageFont.load_default()

def pic(d, p, sl, a, b, c, s):
    if os.path.exists(
    "template.jpg"):
        img = Image.open(
        "template.jpg")
        img = img.convert("RGB")
    else:
        img = Image.new(
        "RGB",
        (800, 1200),
        (20, 20, 20))
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
    box = []
    box.append(x0)
    box.append(y0)
    box.append(x1)
    box.append(y1)
    draw.rounded_rectangle(
    box,
    radius=30,
    fill=(255, 255, 255))
    box2 = []
    box2.append(x0 + 8)
    box2.append(y0 + 8)
    box2.append(x1 - 8)
    box2.append(y1 - 8)
    draw.rounded_rectangle(
    box2,
    radius=25,
    outline=(212, 175, 55),
    width=3)
    cx = W // 2
    f_big = get_font(
    int(W * 0.09))
    f_mid = get_font(
    int(W * 0.055))
    f_small = get_font(
    int(W * 0.05))
    y_big = y0 + int(H * 0.03)
    draw.text(
    (cx, y_big),
    arr,
    font=f_big,
    fill=col,
    anchor="mm")
    y_sila = y0 + int(H * 0.075)
    txt_sila = "Sila: "
    txt_sila += str(s)
    txt_sila += "%"
    draw.text(
    (cx, y_sila),
    txt_sila,
    font=f_small,
    fill=(180, 140, 20),
    anchor="mm")
    y = y0 + int(H * 0.125)
    st = int(H * 0.041)
    t1 = "Vhod: "
    t1 += str(round(p, 2))
    draw.text(
    (cx, y),
    t1,
    font=f_mid,
    fill=(0, 0, 0),
    anchor="mm")
    t2 = "SL: "
    t2 += str(round(sl, 2))
    draw.text(
    (cx, y + st),
    t2,
    font=f_mid,
    fill=(180, 30, 30),
    anchor="mm")
    t3 = "TP1: "
    t3 += str(round(a, 2))
    draw.text(
    (cx, y + st * 2),
    t3,
    font=f_mid,
    fill=(0, 0, 0),
    anchor="mm")
    t4 = "TP2: "
    t4 += str(round(b, 2))
    draw.text(
    (cx, y + st * 3),
    t4,
    font=f_mid,
    fill=(0, 0, 0),
    anchor="mm")
    t5 = "TP3: "
    t5 += str(round(c, 2))
    draw.text(
    (cx, y + st * 4),
    t5,
    font=f_mid,
    fill=(0, 0, 0),
    anchor="mm")
    buf = BytesIO()
    img.save(
    buf,
    format="JPEG",
    quality=92)
    buf.seek(0)
    return buf

def get_data():
    import yfinance as yf
    d15 = yf.download(
    "GC=F",
    period="5d",
    interval="15m",
    progress=False,
    auto_adjust=False)
    if d15.columns.nlevels > 1:
        d15.columns = d15.columns.get_level_values(0)
    d15 = d15.dropna()
    d1h = yf.download(
    "GC=F",
    period="1mo",
    interval="1h",
    progress=False,
    auto_adjust=False)
    if d1h.columns.nlevels > 1:
        d1h.columns = d1h.columns.get_level_values(0)
    d1h = d1h.dropna()
    s = pd.Series(
    d15["Close"].values.flatten())
    s1h = pd.Series(
    d1h["Close"].values.flatten())
    price = float(s.iloc[-1])
    ema50 = float(
    s.ewm(span=50).mean().iloc[-1])
    e200 = float(
    s1h.ewm(span=200).mean().iloc[-1])
    if price > e200:
        trend = "UP"
    else:
        trend = "DOWN"
    delta = s.diff()
    gain = delta.where(
    delta > 0, 0)
    gain = gain.rolling(14).mean()
    loss = -delta.where(
    delta < 0, 0)
    loss = loss.rolling(14).mean()
    g = gain.iloc[-1]
    l = loss.iloc[-1]
    if l != 0:
        rsi = float(
        100 - (100 / (1 + g / l)))
    else:
        rsi = 50.0
    e12 = s.ewm(span=12).mean()
    e26 = s.ewm(span=26).mean()
    macd = e12 - e26
    ms = macd.ewm(span=9).mean()
    ma20 = s.rolling(20).mean()
    sd = s.rolling(20).std()
    bbu = float(
    ma20.iloc[-1] + 2 * sd.iloc[-1])
    bbl = float(
    ma20.iloc[-1] - 2 * sd.iloc[-1])
    hi = d15["High"].values.flatten()
    lo = d15["Low"].values.flatten()
    cl = d15["Close"].values.flatten()
    tr1 = hi[1:] - lo[1:]
    tr2 = abs(hi[1:] - cl[:-1])
    tr3 = abs(lo[1:] - cl[:-1])
    tr = np.maximum(
    tr1,
    np.maximum(tr2, tr3))
    atr = float(
    pd.Series(tr).rolling(14).mean().iloc[-1])
    atr = max(5, min(20, atr))
    h5 = float(s.max())
    l5 = float(s.min())
    f618 = round(
    h5 - (h5 - l5) * 0.618, 2)
    f382 = round(
    h5 - (h5 - l5) * 0.382, 2)
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
        v0 = p - a * 1.5
        sl = round(v0, 2)
        v1 = p + a * 1.2
        t1 = round(v1, 2)
        v2 = p + a * 2.2
        t2 = round(v2, 2)
        v3 = p + a * 3.2
        t3 = round(v3, 2)
        sila = min(95, 65 + buy * 4)
        return "BUY", sila, sl, t1, t2, t3
    if sell >= 5 and sell > buy + 1:
        v0 = p + a * 1.5
        sl = round(v0, 2)
        v1 = p - a * 1.2
        t1 = round(v1, 2)
        v2 = p - a * 2.2
        t2 = round(v2, 2)
        v3 = p - a * 3.2
        t3 = round(v3, 2)
        sila = min(95, 65 + sell * 4)
        return "SELL", sila, sl, t1, t2, t3
    v0 = p - a * 1.5
    sl = round(v0, 2)
    v1 = p + a * 1.2
    t1 = round(v1, 2)
    v2 = p + a * 2.2
    t2 = round(v2, 2)
    v3 = p + a * 3.2
    t3 = round(v3, 2)
    return "WAIT", 45, sl, t1, t2, t3

def chart(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cl = df["Close"].values.flatten()
    op = df["Open"].values.flatten()
    hi = df["High"].values.flatten()
    lo = df["Low"].values.flatten()
    fig, ax = plt.subplots(
    figsize=(10, 5))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    for i in range(len(cl)):
        if cl[i] >= op[i]:
            c = "green"
        else:
            c = "red"
        xs = []
        xs.append(i)
        xs.append(i)
        ys = []
        ys.append(lo[i])
        ys.append(hi[i])
        ax.plot(
        xs,
        ys,
        color=c,
        linewidth=1)
        xs2 = []
        xs2.append(i - 0.3)
        xs2.append(i + 0.3)
        ys2 = []
        ys2.append(op[i])
        ys2.append(op[i])
        ax.plot(
        xs2,
        ys2,
        color=c,
        linewidth=2)
        ys3 = []
        ys3.append(cl[i])
        ys3.append(cl[i])
        ax.plot(
        xs2,
        ys3,
        color=c,
        linewidth=2)
    ema_line = pd.Series(cl).ewm(
    span=50).mean().values
    ax.plot(
    ema_line,
    color="blue",
    linewidth=1.2,
    label="EMA50")
    ax.set_title(
    "SUKHOY - XAUUSD - PRO",
    fontsize=14,
    fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(
    buf,
    format="png",
    dpi=100)
    plt.close()
    buf.seek(0)
    return buf

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(
    m.chat.id,
    "SUKHOY XAUUSD PRO - /check")

@bot.message_handler(commands=["check"])
def check(m):
    bot.send_message(
    m.chat.id,
    "PRO analiz...")
    try:
        d = get_data()
        sig, sila, sl, tp1, tp2, tp3 = calc(d)
        price = d["price"]
    except Exception as e:
        bot.send_message(
        m.chat.id,
        "Oshibka: " + str(e))
        return
    bot.send_photo(
    m.chat.id,
    chart(d["df"]))
    im = pic(
    sig,
    price,
    sl,
    tp1,
    tp2,
    tp3,
    sila)
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
            bot.set_webhook(
            url=APP_URL + "/" + TOKEN)
            print("Webhook set!", flush=True)
    except Exception as e:
        print(
        "Webhook error: " + str(e),
        flush=True)
        traceback.print_exc()
    port = int(
    os.environ.get("PORT", 10000))
    print("Port " + str(port), flush=True)
    app.run(
    host="0.0.0.0",
    port=port)
