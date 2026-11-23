import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

last_signal = ""

def get_gold_price():
    r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15)
    data = r.json()
    item = data["items"][0]
    return float(item["curr"]), float(item["chg"])

def make_signal(price):
    global last_signal
    if price >= 2700:
        signal = "PRODAZHA - Cena ochen vysoko"
    elif price >= 2650:
        signal = "OSTOROZHNO - Cena vysoko, ne pokupaem"
    elif price <= 2600:
        signal = "POKUPKA - Cena nizko, horoshiy vhod"
    elif price <= 2550:
        signal = "SILNAYA POKUPKA - Cena ochen nizko"
    else:
        signal = "ZHDEM - Cena v seredine, bez sdelki"
    if signal == last_signal:
        return None
    last_signal = signal
    return signal

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot aktivnyy zapushchen! Budu slat signaly po zolotu kazhdye 15 minut.\n\nKomandy:\n/start - zapustit\n/price - uznat cenu\n/status - proverit"
    )

async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price, chg = get_gold_price()
        sig = make_signal(price) or "Signal bez izmeneniy"
        await update.message.reply_text(f"ZOLOTO SEYCHAS\nCena: {price:.2f}\nIzmenenie: {chg:+.2f}\n\n{sig}")
    except Exception as e:
        await update.message.reply_text(f"Oshibka: {e}")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ya zhivoy! Proveryayu zoloto kazhdye 15 minut.")

async def check_gold(context: ContextTypes.DEFAULT_TYPE):
    try:
        price, chg = get_gold_price()
        print(f"Price {price} | Chg {chg}", flush=True)
        signal = make_signal(price)
        if signal and CHAT_ID != 0:
            text = f"SIGNAL PO ZOLOTU\n\nCena: {price:.2f}\nIzmenenie: {chg:+.2f}\n\n{signal}"
            await context.bot.send_message(chat_id=CHAT_ID, text=text)
            print("Signal otpravlen!", flush=True)
    except Exception as e:
        print(f"Oshibka proverki: {e}", flush=True)

def main():
    if not TOKEN:
        print("OSHIBKA: Net TELEGRAM_TOKEN!", flush=True)
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    if app.job_queue:
        app.job_queue.run_repeating(check_gold, interval=900, first=10)
        print("Budilnik vklyuchen!", flush=True)
    print("Bot zapushchen!", flush=True)
    app.run_polling()

if __name__ == "__main__":
    main()
