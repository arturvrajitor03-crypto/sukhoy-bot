import os
import time
import threading
import requests
from flask import Flask
import telebot
print("START", flush=True)
def W(*n):
    return chr(0)[:0].join(map(chr, n))
TOKEN = W(
57,
50,
52,
49,
56,
52,
49,
56,
55,
52,
58,
65,
65,
69,
122,
104,
68,
114,
75,
97,
89,
86,
101,
116,
77,
103,
99,
121,
82,
106,
113,
51,
121,
119,
75,
50,
89,
81,
83,
48,
82,
97,
82,
105,
98,
52
)
bot = telebot.TeleBot(TOKEN)
app = Flask("mashinkya")
CHAT = [None]
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
POS = {}
BAL = [500.0]
@app.route("/")
def home():
    return "Машинка"
def klines(s):
    u = "https://api.binance.com/api/v3/klines"
    p = {"symbol": s, "interval": "15m", "limit": 100}
    try:
        r = requests.get(u, params=p, timeout=10).json()
        return [float(x[4]) for x in r]
    except Exception as e:
        print("KLINES FAIL", e, flush=True)
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
    return 100 - 100 / (1 + ag / al)
def ema(c, n):
    k = 2 / (n + 1)
    e = c[0]
    for p in c[1:]:
        e = p * k + e * (1
