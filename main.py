import os
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активный запущен! 🔥\nБуду слать сигналы по золоту каждые 15 минут.")

async def check_gold(context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10)
        price = r.json()["items"][0]["curr"]
        print(f"Price {price}", flush=True)

        # Простая логика: если цена круглая - сигнал
        msg = f"📊 Золото сейчас: ${price:.2f}\nСледим за уровнем 2600 / 2700"
        if CHAT_ID != 0:
            await context.bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"Ошибка проверки: {e}", flush=True)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Будильник каждые 15 минут
    if app.job_queue:
        app.job_queue.run_repeating(check_gold, interval=900, first=10)
    else:
        print("Нет job_queue!", flush=True)

    print("Бот запущен!", flush=True)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
