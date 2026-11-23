import os
import logging
import requests
import threading
import time
import traceback
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0") or "0")
PORT = int(os.getenv("PORT", "10000"))
BALANCE = 500.0
START_BALANCE = 500.0
LOT = 1.00
position = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, *args):
        pass

def get_history():
    urls = [
        "https://api.binance.us/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
        "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            closes = [float(x[4]) for x in r]
            if len(closes) > 50:
                return closes
        except Exception:
            continue
    return []

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0:
        return 100
    rs = ag / al
    return 100 - (100 / (1 + rs))

def calc_ema(closes, period, current_price=None):
    if not closes:
        return current_price if current_price else 0
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p * k + ema * (1 - k)
    return ema

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
        ch = d.get("change24h", 0)
        return float(d["price"]), float(ch)
    except Exception:
        pass
    raise Exception("API ne otvechayut")

def get_tp_sl(pos):
    entry = pos["price"]
    if pos["type"] == "BUY":
        tp = entry * 1.02
        sl = entry * 0.985
    else:
        tp = entry * 0.98
        sl = entry * 1.015
    return tp, sl

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"VIRTUALNIY SCHET\n\nStart: {START_BALANCE:.2f}$\nSeychas: {BALANCE:.2f}$\nPribil: {znak}{profit:.2f}$\nLot: {LOT}\n"
    if position:
        tp, sl = get_tp_sl(position)
        txt += f"\nOtkrita: {position['type']} Lot {position['lot']} po {position['price']:.2f}\nSumma: {position['amount']:.2f}$\nTP: {tp:.2f}\nSL: {sl:.2f}"
    else:
        txt += "\nOtkritih sdelok net"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    msg = f"Bot PRO AKTIVNIY rabotaet!\n\nBUY + SELL\nLot: {LOT}\nVirtual: 500$\n\n/balance - deneg\n/status - pozicii + TP/SL\n/price - cena"
    await update.message.reply_text(msg)

async
