import os
import time
import threading
import requests
import math
import operator as op
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
                if op.gt(len(r), 10):
                    out = []
                    for x in r:
                        out.append(float(x[4]))
                    return out
        except:
            continue
    return []

def rsi(c):
    if op.lt(len(c), 15):
        return 50
    g = []
    l = []
    for i in range(1, len(c)):
        d = c[i] - c[i-1]
        g.append(max(d, 0))
        l.append(max(-d, 0))
    ag = sum(g[-14:]) / 14
    al = sum(l[-14:]) / 14
    if op.eq(al, 0):
        return 100
    return 100 - (100 / (1 + ag / al))

def ema(c, n):
    k = 2 / (n + 1)
    e = c[0]
    for p in c[1:]:
        e = p * k + e * (1 - k)
    return e

def stoch(c):
    if op.lt(len(c), 14):
        return 50
    low = min(c[-14:])
    high = max(c[-14:])
    if op.eq(high, low):
        return 50
    return (c[-1] - low) / (high - low) * 100
