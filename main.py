import os
import time
import threading
import traceback
from flask import Flask
from flask import request
import telebot
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
APP_URL = os.environ.get(
"RENDER_EXTERNAL_URL", "")
APP_URL = APP_URL.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

BAL = 500.0
POS = None
HIST = []
LAST = 0

def get_data():
    import yfinance as yf
    d15 = yf.download(
    "BTC-USD",
    period="5d",
    interval="15m",
    progress=False)
    if d15.columns.nlevels > 1:
        d15.columns = d15.columns.get_level_values(0)
    d15 = d15.dropna()
    d1h = yf.download(
    "BTC-USD",
    period="1mo",
    interval="1h",
    progress=False)
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
    gain = delta.clip(
    lower=0).rolling(14).mean()
    loss = (-delta.clip(
    upper=0)).rolling(14).mean()
    g = float(
    np.array(gain).flatten()[-1])
    l = float(
    np.array(loss).flatten()[-1])
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
    tr1, np.maximum(tr2, tr3))
    atr = float(
    pd.Series(tr).rolling(14).mean().iloc[-1])
    atr = max(200, min(1500, atr))
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
    "macd": float(
    np.array(macd).flatten()[-1]),
    "ms": float(
    np.array(ms).flatten()[-1]),
    "bbu": bbu,
    "bbl": bbl,
    "atr": atr,
    "f618": f618,
    "f382": f382
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
    if buy >= 5 and buy > sell + 1:
        return "BUY", buy
    if sell >= 5 and sell > buy + 1:
        return "SELL", sell
    return "WAIT", buy

def check_trade(chat_id):
    global BAL, POS, LAST
    try:
        d = get_data()
        sig, sila = calc(d)
        p = d["price"]
        if POS is None:
            if sig == "WAIT":
                return
            if time.time() - LAST < 600:
                return
            if sig == "BUY":
                sl = round(p - 600, 2)
                tp = round(p + 900, 2)
            else:
                sl = round(p + 600, 2)
                tp = round(p - 900, 2)
            POS = {
            "side": sig,
            "entry": p,
            "sl": sl,
            "tp": tp
            }
            LAST = time.time()
            bot.send_message(chat_id,
            "DEMO BTC OPEN " + sig +
            "\nVhod: " + str(p) +
            "\nSL: " + str(sl) +
            "\nTP: " + str(tp))
            return
        side = POS["side"]
        entry = POS["entry"]
        sl = POS["sl"]
        tp = POS["tp"]
        close = None
        pnl = 0
        if side == "BUY":
            if p <= sl:
                close = "SL"
                pnl = (sl - entry) * 0.05
            if p >= tp:
                close = "TP"
                pnl = (tp - entry) * 0.05
        else:
            if p >= sl:
                close = "SL"
                pnl = (entry - sl) * 0.05
            if p <= tp:
                close = "TP"
                pnl = (tp - entry) * 0.05
        if close is not None:
            BAL = BAL + pnl
            HIST.append(pnl)
            bot.send_message(chat_id,
            "DEMO BTC CLOSE " + close +
            "\nPnL: " + str(round(pnl, 2)) +
            "\nBalans: " + str(round(BAL, 2)))
            POS = None
    except Exception as e:
        print("ERR " + str(e), flush=True)

def loop(chat_id):
    while True:
        check_trade(chat_id)
        time.sleep(300)

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id,
    "DEMO BTC BOT 500$")

@bot.message_handler(commands=["check"])
def check(m):
    bot.send_message(m.chat.id,
    "Proveryayu BTC...")
    check_trade(m.chat.id)
    if POS is None:
        bot.send_message(m.chat.id,
        "Net sdelki. Balans: " +
        str(round(BAL, 2)))
    else:
        bot.send_message(m.chat.id,
        "Otkrita: " + POS["side"])

@bot.message_handler(commands=["balance"])
def bal(m):
    tot = sum(HIST)
    bot.send_message(m.chat.id,
    "Balans: " + str(round(BAL, 2)) +
    "\nSdelok: " + str(len(HIST)) +
    "\nPnL: " + str(round(tot, 2)))

@bot.message_handler(commands=["auto"])
def auto(m):
    t = threading.Thread(
    target=loop, args=(m.chat.id,),
    daemon=True)
    t.start()
    bot.send_message(m.chat.id,
    "AUTO BTC VKLUCHEN!")

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    data = request.stream.read().decode("utf-8")
    upd = telebot.types.Update.de_json(data)
    bot.process_new_updates([upd])
    return "OK", 200

@app.route("/")
def index():
    return "Demo BTC Bot alive!", 200

if __name__ == "__main__":
    print("=== STARTING ===", flush=True)
    try:
        if os.environ.get("BOT_TOKEN"):
            bot.remove_webhook()
            bot.set_webhook(
            url=APP_URL + "/" + TOKEN)
            print("Webhook set!", flush=True)
    except Exception as e:
        print("Webhook error: " + str(e), flush=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
