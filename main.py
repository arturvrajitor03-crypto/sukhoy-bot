import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sukhoy-bot.onrender.com")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_data():
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "PAXGUSDT", "interval": "15m", "limit": 200}
        r = requests.get(url, timeout=10)
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

def get_signal():
    df = get_data()
    if df is None or len(df) < 60:
        return None
    close = df['Close']
    price = float(close.iloc[-1])
    ema50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
    rsi = calc_rsi(close)
    last_50 = df.tail(50)
    high = float(last_50['High'].max())
    low = float(last_50['Low'].min())
    diff = high - low
    fib_618 = high - diff * 0.618
    fib_382 = high - diff * 0.382
    fib_236 = high - diff * 0.236
    if price < ema50:
        direction = "SELL"
        emoji = "🔴"
        entry = price
        stop = round(fib_382, 2) if fib_382 > price else round(price + 18, 2)
        tp1 = round(fib_236, 2)
        tp2 = round(low, 2)
        tp3 = round(low - 10, 2)
        reason = f"Цена под EMA50 ({ema50:.1f}) - тренд вниз"
    else:
        direction = "BUY"
        emoji = "🟢"
        entry = price
        stop = round(fib_618, 2) if fib_618 < price else round(price - 18, 2)
        tp1 = round(fib_382, 2)
        tp2 = round(high, 2)
        tp3 = round(high + 10, 2)
        reason = f"Цена над EMA50 ({ema50:.1f}) - тренд вверх"
    strength = min(95, max(55, int(abs(price - ema50) / 2 + 60)))
    text = (
        f"👑 СУХОЙ - XAUUSD - {emoji} {direction}\n\n"
        f"💰 Цена: {price:.2f}\n"
        f"📊 RSI: {rsi:.0f} | EMA50: {ema50:.1f} | Сила: {strength}%\n"
        f"📈 {reason}\n"
        f"Fib 0.618: {fib_618:.1f} | Fib 0.382: {fib_382:.1f}\n\n"
        f"Вход: {entry:.2f}\n"
        f"СТОП: {stop:.2f}\n"
        f"ЦЕЛЬ 1: {tp1:.2f}\n"
        f"ЦЕЛЬ 2: {tp2:.2f}\n"
        f"ЦЕЛЬ 3: {tp3:.2f}"
    )
    return text

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👑 Сухой Бот работает!\nНапиши /check для сигнала XAUUSD")

@bot.message_handler(commands=['check'])
def check(message):
    bot.reply_to(message, "⏳ Считаю EMA + RSI + Fib...")
    sig = get_signal()
    if sig:
        bot.reply_to(message, sig)
    else:
        bot.reply_to(message, "❌ Нет данных, попробуй через минуту")

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
        print("Webhook set!")
    except Exception as e:
        print(f"Webhook error: {e}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
