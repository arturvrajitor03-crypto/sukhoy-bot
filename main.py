import os
import logging
import requests
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"TOKEN est? {'DA' if TOKEN else 'NET!'}", flush=True)
CHAT_ID = int(os.getenv("CHAT_ID", "0") or "0")
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
        print("Web server OK", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"Web error: {e}", flush=True)

def get_history():
    urls = [
        "https://api.binance.us/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
        "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
        "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            closes = [float(x[4]) for x in r]
            if len(closes) > 50:
                print(f"History OK iz {url}", flush=True)
                return closes
        except Exception as e:
            print(f"History fail {url}: {e}", flush=True)
            continue
    return []

def calc_rsi(closes, period=14):
    if len(closes) < period+1:
        return 50
    gains, losses = [],
