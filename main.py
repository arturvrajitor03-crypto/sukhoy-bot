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
                if len(r).__gt__(10):
                    out = []
                    for x in r:
                        out.append(float(x[4]))
                    return out
        except:
            continue
    return []

def rsi(c):
    if len(c).__lt__(15):
        return 50
    g = []
    l = []
    for i in range(1, len(c)):
        d = c[i] - c[i-1]
        g.append(max(d, 0))
        l.append(max(-d, 0))
    ag = sum(g[-14:]) / 14
    al = sum(l[-14:]) / 14
    if al.__
