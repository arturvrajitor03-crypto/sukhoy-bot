import os
import time
import threading
import requests
import math
from flask import Flask
import telebot

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
CHAT_ID = None
SYMBOLS = ["BTCUSDT"]
SYMBOLS += ["ETHUSDT"]
SYMBOLS += ["SOLUSDT"]
SYMBOLS += ["BNBUSDT"]
SYMBOLS += ["XRPUSDT"]
SYMBOLS += ["DOGEUSDT"]
positions = {}
balance = 500.0

# Ssylki sobiraem iz kusochkov
# chtoby telefon ne rval ih
H = "https://"
T1 = "testnet.binance"
T2 = ".vision"
B1 = "api.binance"
B2 = ".com"
BASE1 = H + T1 + T2
BASE2 = H + B1 + B2
KLINE = "/api/v3/klines"
PRICE = "/api/v3/ticker/price"

@app.route('/')
def home():
    return "Mashinka ON"

def klines(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + KLINE
            p = {}
            p["symbol"] = s
            p["interval"] = "15m"
            p["limit"] = 100
            r = requests.get(u, params=p, timeout=10)
            r = r.json()
            if isinstance(r, list):
                if len(r) > 10:
                    out = []
                    for x in r:
                        out.append(float(x[4]))
                    return out
        except:
            continue
    return []

def rsi(c):
    if len(c) < 15:
        return 50
    g = []
    l = []
    for i in range(1, len(c)):
        d = c[i] - c[i-1]
        g.append(max(d, 0))
        l.append(max(-d, 0))
    ag = sum(g[-14:]) / 14
    al = sum(l[-14:]) / 14
    if al == 0:
        return 100
    return 100 - (100 / (1 + ag / al))

def ema(c, n):
    k = 2 / (n + 1)
    e = c[0]
    for p in c[1:]:
        e = p * k + e * (1 - k)
    return e

def stoch(c):
    if len(c) < 14:
        return 50
    low = min(c[-14:])
    high = max(c[-14:])
    if high == low:
        return 50
    return (c[-1] - low) / (high - low) * 100

def price(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + PRICE
            p = {}
            p["symbol"] = s
            r = requests.get(u, params=p, timeout=10)
            r = r.json()
            return float(r['price'])
        except:
            continue
    return None

def send(t):
    global CHAT_ID
    if CHAT_ID:
        try:
            bot.send_message(CHAT_ID, t)
        except:
            pass
    print(t)

def analyze(s):
    c = klines(s)
    if not c:
        return None
    p = c[-1]
    r = rsi(c)
    e20 = ema(c, 20)
    e50 = ema(c, 50)
    st = stoch(c)
    m = ema(c, 12) - ema(c, 26)
    score = 0
    det = []
    if r < 50:
        score += 1
        det.append("RSI OK")
    else:
        det.append("RSI NO")
    if p > e20:
        score += 1
        det.append("EMA OK")
    else:
        det.append("EMA NO")
    if e20
