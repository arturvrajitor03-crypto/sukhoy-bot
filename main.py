import os, logging, threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Sukhoy Bot Live XAUUSD"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! ✅\nПиши /dry")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Рисую XAUUSD 15м...")
    try:
        # Тестовые данные чтобы проверить бота (потом подключим реальный рынок)
        x = np.arange(80)
        price = 4000 + np.cumsum(np.random.randn(80)*2)
        
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(price, linewidth=2, color='black')
        high = price.max()
        low = price.min()
        last = price[-1]
        ax.axhline(high, color='red', linestyle='--', label=f'HIGH {high:.2f}')
        ax.axhline(low, color='green', linestyle='--', label=f'LOW {low:.2f}')
        ax.set_title(f"XAUUSD 15m TEST | Last {last:.2f}", fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.savefig("chart.png", dpi=150)
        plt.close()
        
        with open("chart.png", "rb") as f:
            await update.message.reply_photo(f, caption=f"✅ БОТ ЗАРАБОТАЛ!\nLast: {last:.2f}\nHigh: {high:.2f}\nLow: {low:.2f}\n\nЭто тест. Скажи - видишь картину? Подключу реальные данные!")
    except Exception as e:
        logging.error(f"ERROR: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dry", dry))
    print("Bot polling started")
    app.run_polling()

if __name__ == "__main__":
    main()
