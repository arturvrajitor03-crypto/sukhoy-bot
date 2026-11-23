import os
import logging
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))
PORT = int(os.getenv("PORT", "10000"))

last_signal = ""

# --- FAKE WEB SERVER DLYA RENDER ---
# Render trebuet otkrytyy port, inache pishet "No open ports"
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
        print(f"Web server started on port {PORT}", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"Web server error: {e}", flush=True)

# --- ZOLOTO ---
def get_gold_price():
    r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15)
    data = r.json()
    item = data["items"][0]
    return float(item["curr"]), float(item["chg"])

def make_signal(price):
    global last_signal
    if price >= 2700:
        signal = "PRODAZHA - Cena ochen vysoko, zhdem otkat"
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

    # Zapuskaem fake web server v fone, chtoby Render ne rugalsya na porty
    threading.Thread(target=run_web
