import os
import asyncio
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler

logging.basicConfig(
    level=logging.INFO
)

TOKEN = os.getenv(
    "BOT_TOKEN", ""
).strip()

print(
    f"TOKEN={bool(TOKEN)}",
    flush=True
)

app = Flask(__name__)

@app.route('/')
def home():
    return f"OK {bool(TOKEN)}"

async def start(update, context):
    await update.message.reply_text(
        "Привет! Работаю!"
    )

async def status(update, context):
    await update.message.reply_text(
        "Online!"
    )

def run_bot():
    if not TOKEN:
        print("No token!", flush=True)
        return
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(
            "Starting polling...",
            flush=True
        )
        a = Application.builder().token(
            TOKEN
        ).build()
        a.add_handler(
            CommandHandler("start", start)
        )
        a.add_handler(
            CommandHandler("status", status)
        )
        print("Polling OK!", flush=True)
        a.run_polling(
            stop_signals=None
        )
    except Exception as e:
        print(f"Err: {e}", flush=True)

print("Init thread...", flush=True)
t = threading.Thread(
    target=run_bot,
    daemon=True
)
t.start()

if __name__ == '__main__':
    p = int(os.getenv("PORT", "10000"))
    app.run(
        host='0.0.0.0',
        port=p
    )
