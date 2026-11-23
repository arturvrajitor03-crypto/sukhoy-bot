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

SYMBOLS = {
    "ЗОЛОТО": "PAXGUSDT",
    "БИТКОИН": "BTCUSDT",
    "ЭФИРИУМ": "ETHUSDT",
    "НЕФТЬ": "CL=F",
}
positions = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, *args):
        pass

def get_history(symbol):
    if symbol == "CL=F":
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=15m&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, timeout=10, headers=headers).json()
            closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [float(x) for x in closes if x is not None]
            return closes
        except Exception:
            return []
    urls = [
        f"https://api.binance.us/api/v3/klines?symbol={symbol}&interval=15m&limit=100",
        f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit=100",
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

def calc_ema(closes, period):
    if not closes:
        return 0
    if len(closes) < period:
        return closes
