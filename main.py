import os, logging, threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "XAUUSD 15m ACCURATE Bot LIVE!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_accurate_chart():
    # 15 минут - точные данные XAUUSD
    df = yf.download("GC=F", period="5d", interval="15m", auto_adjust=True)
    if len(df) < 100:
        df = yf.download("GC=F", period="7d", interval="15m", auto_adjust=True)
    
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['RSI'] = rsi(df['Close'], 14)
    df = df.dropna()

    buys = []
    sells = []
    for i in range(1, len(df)):
        price = float(df['Close'].iloc[i])
        ema9 = float(df['EMA9'].iloc[i])
        ema21 = float(df['EMA21'].iloc[i])
        ema50 = float(df['EMA50'].iloc[i])
        rsi_val = float(df['RSI'].iloc[i])
        ema9_prev = float(df['EMA9'].iloc[i-1])
        ema21_prev = float(df['EMA21'].iloc[i-1])

        # ТОЧНЫЙ БАЙ: пересечение вверх + RSI >55 + выше EMA50
        if ema9_prev < ema21_prev and ema9 > ema21 and rsi_val > 55 and price > ema50:
            buys.append(i)
        # ТОЧНЫЙ СЕЛЛ: пересечение вниз + RSI <45 + ниже EMA50
        if ema9_prev > ema21_prev and ema9 < ema21 and rsi_val < 45 and price < ema50:
            sells.append(i)

    # Рисуем только последние 120 свечей 15м
    df_plot = df.tail(120)
    offset = len(df) - len(df_plot)
    buys_plot = [b - offset for b in buys if b >= offset]
    sells_plot = [s - offset for s in sells if s >= offset]

    plt.figure(figsize=(11,6))
    plt.plot(df_plot['Close'].values, label='XAUUSD 15m', color='black', linewidth=2)
    plt.plot(df_plot['EMA9'].values, label='EMA9', color='#2962FF', linewidth=1.1, alpha=0.7)
    plt.plot(df_plot['EMA21'].values, label='EMA21', color='#FF6D00', linewidth=1.1, alpha=0.7)
    plt.plot(df_plot['EMA50'].values, label='EMA50 Trend', color='gray', linewidth=1, linestyle='--')

    for b in buys_plot:
        plt.scatter(b, df_plot['Close'].iloc[b], marker='^', color='#00C853', s=180, zorder=5, edgecolors='white', linewidth=1.5)
        plt.text(b, float(df_plot['Close'].iloc[b])-2, '✅ BUY', color='#00C853', fontweight='bold', ha='center', fontsize=9)

    for s in sells_plot:
        plt.scatter(s, df_plot['Close'].iloc[s], marker='v', color='#D50000', s=180, zorder=5, edgecolors='white', linewidth=1.5)
        plt.text(s, float(df_plot['Close'].iloc[s])+2, '✅ SELL', color='#D50000', fontweight='bold', ha='center', fontsize=9)

    plt.title(f'XAUUSD 15m ACCURATE - {len(buys_plot)} BUY / {len(sells_plot)} SELL (Filtered)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('chart.png', dpi=180)
    plt.close()

    last_rsi = float(df['RSI'].iloc[-1])
    last_diff = float(df['EMA9'].iloc[-1] - df['EMA21'].iloc[-1])
    price = float(df['Close'].iloc[-1])

    if 0 < last_diff < 0.8 and last_rsi > 50:
        soon = f"⚠️ СКОРО БАЙ! RSI={last_rsi:.1f} Цена подходит"
    elif -0.8 < last_diff < 0 and last_rsi < 50:
        soon = f"⚠️ СКОРО СЕЛЛ! RSI={last_rsi:.1f} Цена подходит"
    elif last_diff > 0.8:
        soon = f"🟢 Тренд БАЙ (RSI {last_rsi:.1f}) - держим лонг"
    else:
        soon = f"🔴 Тренд СЕЛЛ (RSI {last_rsi:.1f}) - держим шорт"

    return soon, len(buys_plot), len(sells_plot), price, last_rsi

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот XAUUSD 15m Точный 🥇\n/dry - картина с точными сигналами ✅")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анализирую XAUUSD 15м... 🔍 Фильтрую ложные сигналы...")
    try:
        soon, b_cnt, s_cnt, price, rsi_v = get_accurate_chart()
        caption = f"🔥 XAUUSD 15m = {price:.2f} $ | RSI {rsi_v:.1f}\n\n{soon}\n\n✅ Точных БАЙ: {b_cnt}\n✅ Точных СЕЛЛ: {s_cnt}\n\nКаждая галочка = прошла 3 фильтра (EMA+RSI+Trend)"
        with open('chart.png', 'rb') as f:
            await update.message.reply_photo(photo=f, caption=caption)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dry", dry))
    app.add_handler(CommandHandler("signal", dry))
    app.add_handler(CommandHandler("xau", dry))
    app.run_polling()
