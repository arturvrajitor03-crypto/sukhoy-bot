import os
import logging
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))
PORT = int(os.getenv("PORT", "10000"))
last_signal = ""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, *args):
        pass

def run_web_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), Handler)
        print("Web server started", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"Web error: {e}", flush=True)

def get_gold_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10, headers=headers)
        data = r.json()
        item = data["items"][0]
        return float(item["curr"]), float(item["chg"])
    except Exception as e:
        print(f"API 1 fail: {e}", flush=True)
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10, headers=headers)
        data = r.json()
        price = float(data["price"])
        chg = float(data.get("change24h", 0))
        return price, chg
    except Exception as e:
        print(f"API 2 fail: {e}", flush=True)
    try:
        r = requests.get("https://api.metals.live/v1/spot", timeout=10, headers=headers)
        data = r.json()
        price = float(data["gold"])
        return price, 0.0
    except Exception as e:
        print(f"API 3 fail: {e}", flush=True)
    raise Exception("Vse API ne otvechayut")

def make_signal(price):
    global last_signal
    if price >= 3750:
        signal = "PRODAZHA - Cena ochen vysoko, zhdem otkat"
    elif price >= 3680:
        signal = "OSTOROZHNO - Cena vysoko, ne pokupaem"
    elif price <= 3580:
        signal = "POKUPKA - Cena nizko, horoshiy vhod"
    elif price <= 3520:
        signal = "SILNAYA POKUPKA - Cena ochen nizko"
    else:
        signal = "ZHDEM - Cena v seredine, bez sdelki"
    if signal == last_signal:
        return None
    last_signal = signal
    return signal

async def start(update, context):
    await update.message.reply_text("Bot zapushchen! Signaly po zolotu kazhdye 15 minut.\n\n/start - zapustit\n/price - cena\n/status - proverit")

async def price_cmd(update, context):
    try:
        price, chg = get_gold_price()
        sig = make_signal(price) or "Bez izmeneniy"
        txt = f"ZOLOTO SEYCHAS\nCena: {price:.2f}\nIzm: {chg:+.2f}\n\n{sig}"
        await update.message.reply_text(txt)
    except Exception as e:
        await update.message.reply_text(f"Oshibka: {e}")

async def status_cmd(update, context):
    await update.message.reply_text("Ya zhivoy! Proveryayu zoloto kazhdye 15 minut.")

async def check_gold(context):
    try:
        price, chg = get_gold_price()
        print(f"Price {price}", flush=True)
        signal = make_signal(price)
        if signal and CHAT_ID != 0:
            txt = f"SIGNAL PO ZOLOTU\n\nCena: {price:.2f}\nIzm: {chg:+.2f}\n\n{signal}"
            await context.bot.send_message(chat_id=CHAT_ID, text=txt)
    except Exception as e:
        print(f"Oshibka: {e}", flush=True)

def main():
    if not TOKEN:
        print("Net TOKEN!", flush=True)
        return
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    if app.job_queue:
        app.job_queue.run_repeating(check_gold, interval=900, first=10)
    print("Bot zapushchen!", flush=True)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
