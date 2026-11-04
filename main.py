import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update, context):
    await update.message.reply_text("Бот работает! ✅ Токен настроен!")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Bot started polling...")
    application.run_polling()

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing!")
        # Запускаем Flask чтобы Render не ругался
        run_flask()
    else:
        # Flask в фоне, бот в главном потоке
        threading.Thread(target=run_flask, daemon=True).start()
        run_bot()
