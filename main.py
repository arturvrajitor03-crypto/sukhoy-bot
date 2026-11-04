import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
print(f"TOKEN exists={bool(BOT_TOKEN)}")

app = Flask(__name__)

@app.route('/')
def home():
    return f"OK {bool(BOT_TOKEN)}"

async def start(update: Update, context):
    await update.message.reply_text("Привет! ✅ Работаю!")

async def status(update: Update, context):
    await update.message.reply_text("✅ Online!")

def run_bot():
    if not BOT_TOKEN:
        print("No token!")
        return
    print("Starting polling...")
    a = Application.builder().token(BOT_TOKEN).build()
    a.add_handler(CommandHandler("start", start))
    a.add_handler(CommandHandler("status", status))
    print("Polling OK!")
    a.run_polling()

print("Init thread...")
t = threading.Thread(
    target=run_bot,
    daemon=True
)
t.start()

if __name__ == '__main__':
    port = int(os.getenv("PORT", "10000"))
    app.run(
        host='0.0.0.0',
        port=port
    )
