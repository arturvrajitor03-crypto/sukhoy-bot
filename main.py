import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot alive!", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! ✅\n/dry - сигналы")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("SELL 3982 BUY 3958\nСухой: -12")

def run_bot():
    if not TOKEN:
        print("ERROR: BOT_TOKEN missing!")
        return
    print("Starting bot...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dry", dry))
    app.run_polling()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
