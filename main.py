import os, time, threading, requests, math
from flask import Flask
import telebot

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
CHAT_ID = None
SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT"]
positions = {}
balance = 500.0

@app.route('/')
def home():
    return "Mashinka FINAL ON"

def klines(s):
    # Probue testnet, esli net - osnovnoy Binance
    for base in ["https://testnet.binance.vision", "https://api.binance.com"]:
        try:
            u = base + "/api/v3/klines"
            p = {"symbol": s, "interval": "15m", "limit": 100}
            r = requests.get(u, params=p, timeout=10).json()
            if isinstance(r, list) and len(r) > 10:
                return [float(x[4]) for x in r]
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

def macd(c):
    if len(c) < 26:
        return 0, 0
    e12 = ema(c, 12)
    e26 = ema(c, 26)
    # uproshenny MACD
    return e12 - e26, 0

def price(s):
    for base in ["https://testnet
