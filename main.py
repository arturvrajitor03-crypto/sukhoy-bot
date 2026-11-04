import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логов
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
print(f"TOKEN check: exists={bool(BOT_TOKEN)} len={len(BOT_TOKEN)}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Sukhoy Bot is running! Token OK: " + str(bool(BOT_TOKEN))

# --- Команды бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Sukhoy Bot ✅ Работаю!\n/status - проверить")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Online! Деплой 84feb00 работает")

def run_bot():
    if not BOT_TOKEN:
        print("CRITICAL: BOT_TOKEN is missing! Add it in Render -> Environment")
        return
    
    print("Starting polling...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    
    print("Polling started successfully!")
    application.run_polling()

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Запускаем Flask (нужен для Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
