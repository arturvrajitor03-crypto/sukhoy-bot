import os
import random
import traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np

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
    draw.text((cx, y0 + int(H*0.03)), arrow, font=f_dir, fill=col, anchor="mm")
    draw.text((cx, y0 + int(H*0.075)), f"Сила: {sila}%", font=f_sila, fill=(180, 140, 20), anchor="mm")
    y = y0 + int(H*0.125)
    step = int(H*0.041)
    draw.text((cx, y), f"Вход: {price:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step), f"SL: {sl:.2f}", font=f_line, fill=(180, 30, 30), anchor="mm")
    draw.text((cx, y+step*2), f"TP1: {tp1:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*3), f"TP2: {tp2:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y+step*4), f"TP3: {tp3:.2f}", font=f_line, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, y1 - int(H*0.02)), "СУХОЙ - XAUUSD - PRO - Risk 1% - RR 1:2", font=f_small, fill=(120, 120, 120), anchor="mm")
    buf = BytesIO(); img.save(buf, format="JPEG", quality=92); buf.seek(0)
    return buf

def get_pro_data():
    import yfinance as yf
    # 15m - для входа
    df15 = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=False)
    if hasattr(df15.columns, "nlevels") and df15.columns.nlevels > 1:
        df15.columns = df15.columns.get_level_values(0)
    df15 = df15.dropna()
    # 1h - для главного тренда
    df1h = yf.download("GC=F", period="1mo", interval="1h", progress=False, auto_adjust=False)
    if hasattr(df1h.columns, "nlevels") and df1h.columns.nlevels > 1:
        df1h.columns = df1h.columns.get_level_values(0)
    df1h = df1h.dropna()
    s = pd.Series(df15["Close"].values.flatten())
    s1h = pd.Series(df1h["Close"].values.flatten())
    price = float(s.iloc[-1])
    ema50 = float(s.ewm(span=50).mean().iloc[-1])
    ema200_1h = float(s1h.ewm(span=200).mean().iloc[-1])
    trend_1h = "UP" if price > ema200_1h else "DOWN"
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = float(100 - (100 / (1 + rs.iloc[-1])))
    ema12 = s.ewm(span=12).mean(); ema26 = s.ewm(span=26).mean()
    macd = ema12 - ema26; macd_sig = macd.ewm(span=9).mean()
    macd_val = float(macd.iloc[-1]); macd_sig_val = float(macd_sig.iloc[-1])
    ma20 = s.rolling(20).mean(); std20 = s.rolling(20).std()
    bb_up = float(ma20.iloc[-1] + 2*std20.iloc[-1]); bb_low = float(ma20.iloc[-1] - 2*std20.iloc[-1])
    high = df15["High"].values.flatten(); low = df15["Low"].values.flatten(); closes = df15["Close"].values.flatten()
    tr = np.maximum(high[1:]-low[1:], np.maximum(abs(high[1:]-closes[:-1]), abs(low[1:]-closes[:-1])))
    atr = float(pd.Series(tr).rolling(14).mean().iloc[-1])
    if atr < 1: atr = 5.0
    if atr > 20: atr = 20.0
    high5 = float(s.max()); low5 = float(s.min())
    fib618 = round(high5 - (high5 - low5) * 0.618, 2)
    fib382 = round(high5 - (high5 - low5) * 0.382, 2)
    return {"price": price, "ema50": ema50, "ema200_1h": ema200_1h, "trend_1h": trend_1h,
            "rsi": rsi, "macd": macd_val, "macd_sig": macd_sig_val, "bb_up": bb_up, "bb_low": bb_low,
            "atr": atr, "fib618": fib618, "fib382": fib382, "df": df15}

def calc_pro_signal(d):
    price = d["price"]; buy = 0; sell = 0
    # ГЛАВНЫЙ ФИЛЬТР - 1ч тренд, 3 балла
    if d["trend_1h"] == "UP":
        buy += 3
    else:
        sell += 3
    # 15м EMA
    if price > d["ema50"]: buy += 1
    else: sell += 1
    # MACD
    if d["macd"] > d["macd_sig"]: buy += 1
    else: sell += 1
    # RSI - идеальная зона
    if 50 < d["rsi"] < 68: buy += 1
    elif 32 < d["rsi"] < 50: sell += 1
    # Bollinger отбой
    if price <= d["bb_low"]*1.002: buy += 1
    elif price >= d["bb_up"]*0.998: sell += 1
    # Fib
    if abs(price - d["fib618"]) < d["atr"]: buy += 1
    if abs(price - d["fib382"]) < d["atr"]: sell += 1
    atr = d["atr"]
    # Нужно 5 из 7 и совпадение с 1ч
    if buy >= 5 and buy > sell + 1:
        sila = min(95, 65 + buy*4)
        sl = round(price - atr*1.5, 2)
        tp1 = round(price + atr*1.2, 2); tp2 = round(price + atr*2.2, 2); tp3 = round(price + atr*3.2, 2)
        return "BUY", sila, sl, tp1, tp2, tp3
    if sell >= 5 and sell > buy + 1:
        sila = min(95, 65 + sell*4)
        sl = round(price + atr*1.5, 2)
        tp1 = round(price - atr*1.2, 2); tp2 = round(price - atr*2.2, 2); tp3 = round(price - atr*3.2, 2)
        return "SELL", sila, sl, tp1, tp2, tp3
    sila = 45
    sl = round(price - atr*1.5, 2)
    tp1 = round(price + atr*1.2, 2); tp2 = round(price + atr*2.2, 2); tp3 = round(price + atr*3.2, 2)
    return "WAIT", sila, sl, tp1, tp2, tp3

def make_chart(df, ema50, fib618, fib382):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    closes = df["Close"].values.flatten()
    opens = df["Open"].values.flatten()
    highs = df["High"].values.flatten()
    lows = df["Low"].values.flatten()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("white"); fig.patch.set_facecolor("white")
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
    ax.set_title("SUKHOY - XAUUSD - 15m - PRO", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left"); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = BytesIO(); plt.savefig(buf, format="png", dpi=100); plt.close(); buf.seek(0)
    return buf

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "👑 <b>СУХОЙ • XAUUSD • PRO</b>\n\nНапиши /check - самый точный сигнал\nИли выбери раздел:", parse_mode="HTML", reply_markup=kb_main())

@bot.message_handler(commands=["check"])
def check(m):
    bot.send_message(m.chat.id, "⌛ PRO анализ... 1ч тренд + 15м вход + MACD + RSI + BB + Fib + ATR")
    try:
        d = get_pro_data()
        signal, sila, sl, tp1, tp2, tp3 = calc_pro_signal(d)
        price = d["price"]
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка данных: {e}")
        return
    img_chart = make_chart(d["df"], d["ema50"], d["fib618"], d["fib382"])
    bot.send_photo(m.chat.id, img_chart)
    img_lux = make_signal_from_template(signal, price, sl, tp1, tp2, tp3, sila=sila)
    if img_lux:
        bot.send_photo(m.chat.id, img_lux)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "back":
        bot.edit_message_text("👑 <b>СУХОЙ • XAUUSD</b>\n\nВыбери раздел:", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_main())
    elif c.data == "signal":
        price = round(random.uniform(3500, 3530), 2)
        is_buy = random.choice([True, False])
        direction = "BUY" if is_buy else "SELL"
        sila = 80 if is_buy else 65
        sl = round(price - 10 if is_buy else price + 10, 2)
        tp1 = round(price + 10 if is_buy else price - 10, 2)
        tp2 = round(price + 20 if is_buy else price - 20, 2)
        tp3 = round(price + 30 if is_buy else price - 30, 2)
        img = make_signal_from_template(direction, price, sl, tp1, tp2, tp3, sila=sila)
        if img:
            bot.send_photo(c.message.chat.id, img, reply_markup=kb_back())
        else:
            bot.send_message(c.message.chat.id, "Нет шаблона template.jpg")
    elif c.data == "analytics":
        bot.edit_message_text("📈 <b>Аналитика PRO</b>\n\n1ч тренд + 15м вход. Сигнал только если совпадают. 5+ баллов из 7.", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "news":
        bot.edit_message_text("📰 <b>Новости</b>\n\n• Доллар под давлением\n• Золото - защитный актив\n• Сегодня: данные по инфляции США в 15:30", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "vip":
        bot.edit_message_text("💎 <b>VIP</b>\n\n• Сигналы раньше всех\n• Точные TP/SL\n• Личная поддержка\n\nПиши: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    elif c.data == "help":
        bot.edit_message_text("❓ <b>Помощь</b>\n\nНажми /check - мощный сигнал.\nВопросы: @vrajitor", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb_back())
    bot.answer_callback_query(c.id)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def index():
    return "Sukhoy Bot is alive!", 200

if __name__ == "__main__":
    print("=== STARTING SUKHOY BOT ===", flush=True)
    print(f"TOKEN exists: {bool(os.environ.get('BOT_TOKEN'))}", flush=True)
    print(f"APP_URL: {APP_URL}", flush=True)
    print(f"PORT env: {os.environ.get('PORT')}", flush=True)
    try:
        if os.environ.get("BOT_TOKEN"):
            try:
                bot.remove_webhook()
                bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
                print("Webhook set!", flush=True)
            except Exception as e:
                print(f"Webhook error: {e}", flush=True)
                traceback.print_exc()
        else:
            print("!!! BOT_TOKEN ПУСТОЙ !!!", flush=True)
    except Exception as e:
        print(f"Ошибка: {e}", flush=True)
        traceback.print_exc()
    port = int(os.environ.get("PORT", 10000))
    print(f"Запускаю Flask на порту {port}...", flush=True)
    app.run(host="0.0.0.0", port=port)
