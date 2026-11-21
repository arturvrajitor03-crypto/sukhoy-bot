import os
import io
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

def make_chart(df, ema_series, direction, entry, stop, tp1, tp2, tp3):
    # Берем последние 60 свечей для картинки
    plot_df = df.tail(60).reset_index(drop=True)
    ema_plot = ema_series.tail(60).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    # Свечи
    for i, row in plot_df.iterrows():
        color = '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
        ax.plot([i, i], [row['Low'], row['High']], color=color, linewidth=1)
        ax.add_patch(plt.Rectangle((i-0.35, min(row['Open'], row['Close'])),
            0.7, abs(row['Close']-row['Open']),
            facecolor=color, edgecolor=color))
    
    # EMA50
    ax.plot(ema_plot.values, color='#2196f3', linewidth=1.8, label='EMA50')
    
    # Линии вход / стоп / цели
    ax.axhline(entry, color='white', linestyle='--', linewidth=1.2, label=f'Вход {entry:.2f}')
    ax.axhline(stop, color='#ef5350', linestyle='-', linewidth=1.4, label=f'СТОП {stop:.2f}')
    ax.axhline(tp1, color='#26a69a', linestyle=':', linewidth=1.2, label=f'ЦЕЛЬ 1 {tp1:.2f}')
    ax.axhline(tp2, color='#26a69a', linestyle=':', linewidth=1.2, label=f'ЦЕЛЬ 2 {tp2:.2f}')
    ax.axhline(tp3, color='#26a69a', linestyle=':', linewidth=1.2, label=f'ЦЕЛЬ 3 {tp3:.2f}')
    
    # Стрелка сигнала на последней свече
    last_x = len(plot_df)-1
    if direction == "BUY":
        ax.annotate('▲ BUY', xy=(last_x, entry), xytext=(last_x-8, entry-25),
            color='#26a69a', fontsize=14, fontweight='bold',
            arrowprops=dict(facecolor='#26a69a', arrowstyle='->', lw=2))
    elif direction == "SELL":
        ax.annotate('▼ SELL', xy=(last_x, entry), xytext=(last_x-8, entry+25),
            color='#ef5350', fontsize=14, fontweight='bold',
            arrowprops=dict(facecolor='#ef5350', arrowstyle='->', lw=2))
    
    ax.set_title('👑 СУХОЙ - XAUUSD - 15m', color='white', fontsize=14, fontweight='bold', loc='left')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.legend(facecolor='#0e1117', edgecolor='#333333', labelcolor='white', fontsize=8, loc='upper left')
    ax.grid(True, color='#222222', linewidth=0.5)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#0e1117', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def get_signal():
    df = get_data()
    if df is None or len(df) < 60:
        return None, None
    close = df['Close']
    price = float(close.iloc[-1])
    ema_series = close.ewm(span=50, adjust=False).mean()
    ema50 = float(ema_series.iloc[-1])
    rsi = float(calc_rsi(close))
    last_50 = df.tail(50)
    high = float(last_50['High'].max())
    low = float(last_50['Low'].min())
    diff = high - low
    fib_618 = high - diff * 0.618
    fib_382 = high - diff * 0.382
    fib_236 = high - diff * 0.236

    # --- ПРАВИЛЬНАЯ ЛОГИКА ---
    # Не продаем в перепроданности, не покупаем в перекупленности
    if rsi < 30:
        direction = "WAIT"
        emoji = "⏳"
        reason = f"RSI {rsi:.0f} - перепродан, SELL запрещён, ждём отскок вверх"
        entry, stop, tp1, tp2, tp3 = price, round(price + 18, 2), round(price+10,2), round(price+20,2), round(price+30,2)
        strength = 45
    elif rsi > 70:
        direction = "WAIT"
        emoji = "⏳"
        reason = f"RSI {rsi:.0f} - перекуплен, BUY запрещён, ждём откат вниз"
        entry, stop, tp1, tp2, tp3 = price, round(price - 18, 2), round(price-10,2), round(price-20,2), round(price-30,2)
        strength = 45
    elif price < ema50 and 35 <= rsi <= 50:
        direction = "SELL"
        emoji = "🔴"
        entry = price
        stop = round(fib_382, 2) if fib_382 > price else round(price + 18, 2)
        tp1 = round(fib_236, 2)
        tp2 = round(low, 2)
        tp3 = round(low - 10, 2)
        reason = f"Цена под EMA50 ({ema50:.1f}) + RSI {rsi:.0f} - тренд вниз, есть сила"
        strength = min(90, max(60, int(60 + abs(price - ema50)/2 + (50-rsi)/2)))
    elif price > ema50 and 50 <= rsi <= 65:
        direction = "BUY"
        emoji = "🟢"
        entry = price
        stop = round(fib_618, 2) if fib_618 < price else round(price - 18, 2)
        tp1 = round(fib_382, 2)
        tp2 = round(high, 2)
        tp3 = round(high + 10, 2)
        reason = f"Цена над EMA50 ({ema50:.1f}) + RSI {rsi:.0f} - тренд вверх, есть сила"
        strength = min(90, max(60, int(60 + abs(price - ema50)/2 + (rsi-50)/2)))
    else:
        direction = "WAIT"
        emoji = "⏳"
        reason = f"Нет чёткого сигнала: Цена {price:.1f} / EMA50 {ema50:.1f} / RSI {rsi:.0f} - лучше пропустить"
        entry, stop, tp1, tp2, tp3 = price, round(price + 18, 2), round(price+10,2), round(price+20,2), round(price+30,2)
        strength = 50

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
    # Картинку делаем только если есть BUY/SELL, для WAIT тоже делаем - чтобы видеть почему ждем
    img = make_chart(df, ema_series, direction, entry, stop, tp1, tp2, tp3)
    return text, img

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👑 Сухой Бот работает!\nНапиши /check для сигнала XAUUSD с картинкой")

@bot.message_handler(commands=['check'])
def check(message):
    bot.reply_to(message, "⏳ Считаю EMA + RSI + Fib + рисую график...")
    text, img = get_signal()
    if text and img:
        bot.send_photo(message.chat.id, img, caption=text)
    elif text:
        bot.reply_to(message, text)
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
