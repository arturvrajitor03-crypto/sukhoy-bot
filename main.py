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

BALANCE = 500.0
START_BALANCE = 500.0
TRADE_AMOUNT = 50.0
position = None

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
        server.serve_forever()
    except Exception as e:
        print(f"Web error: {e}", flush=True)

def get_history():
    # Berem istoriyu PAXG - eto zoloto na Binance, dlya indikatorov
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        return closes
    except Exception as e:
        print(f"History fail: {e}", flush=True)
        return []

def calc_rsi(closes, period=14):
    if len(closes) < period+1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i]-closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:])/period
    al = sum(losses[-period:])/period
    if al == 0:
        return 100
    rs = ag/al
    return 100 - (100/(1+rs))

def calc_ema(closes, period):
    if len(closes) < period:
        return closes[-1] if closes else 0
    k = 2/(period+1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p*k + ema*(1-k)
    return ema

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0
    ema12 = calc_ema(closes[-30:], 12)
    ema26 = calc_ema(closes[-30:], 26)
    macd = ema12 - ema26
    # signal - EMA9 ot MACD priblizitelno
    return macd, macd

def get_gold_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10, headers=headers)
        item = r.json()["items"][0]
        return float(item["curr"]), float(item["chg"])
    except Exception:
        pass
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10, headers=headers)
        d = r.json()
        return float(d["price"]), float(d.get("change24h", 0))
    except Exception:
        pass
    raise Exception("API ne otvechayut")

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"VIRTUALNIY SCHET\n\nStart: {START_BALANCE:.2f}$\nSeychas: {BALANCE:.2f}$\nPribil: {znak}{profit:.2f}$\n"
    if position:
        txt += f"\nOtkrita: POKUPKA {position['amount']}$ po {position['price']:.2f}"
    else:
        txt += "\nOtkritih sdelok net"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text(f"Bot PRO zapushchen!\n\nIndikatori: RSI + EMA50 + MACD\nVirtual: 500$\nSdelka: 50$\n\n/balance - deneg\n/status - pozicii\n/price - cena + indikatori")

async def balance_cmd(update, context):
    await update.message.reply_text(balance_text())

async def status_cmd(update, context):
    await update.message.reply
