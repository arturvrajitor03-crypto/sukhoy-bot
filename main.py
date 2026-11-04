import os, logging, threading, yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Sukhoy Bot Live XAUUSD 15m"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! ✅\nПиши /dry")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Гружу XAUUSD 15м...")
    try:
        data = yf.download("GC=F", period="2d", interval="15m", progress=False)
        if data.empty:
            data = yf.download("XAUUSD=X", period="2d", interval="15m", progress=False)
        if data.empty:
            await update.message.reply_text("Yahoo не отдает данные, попробуй через 2 мин")
            return
        
        data = data.tail(80)
        close = data['Close']
        if isinstance(close, plt.matplotlib.pandas.DataFrame if False else type(data['Close'])): pass
        
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(data.index, data['Close'], linewidth=2, color='black')
        high = float(data['High'].max())
        low = float(data['Low'].min())
        last = float(data['Close'].iloc[-1])
        
        ax.axhline(high, color='red', linestyle='--', alpha=0.8, label=f'HIGH {high:.2f}')
        ax.axhline(low, color='green', linestyle='--', alpha=0.8, label=f'LOW {low:.2f}')
        ax.axhline(last, color='blue', linestyle=':', alpha=0.6)
        ax.set_title(f"XAUUSD 15m | Last {last:.2f} | Сухой режим", fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig("chart.png", dpi=150)
        plt.close()
        
        with open("chart.png", "rb") as f:
            await update.message.reply_photo(f, caption=f"🔥 XAUUSD 15m\nLast: {last:.2f}\nHigh: {high:.2f}\nLow: {low:.2f}\n✅ Точные уровни с графика!")
    except Exception as e:
        logging.error(f"ERROR: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dry", dry))
    print("Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
