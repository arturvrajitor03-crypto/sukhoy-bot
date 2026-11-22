import os
import time
import threading
import requests
import math
import operator as op
from flask import Flask
import telebot
def W(*n):
    return chr(0)[:0].join(map(chr, n))
TOKEN = os.environ.get(W(84,79,75,69,78))
bot = telebot.TeleBot(TOKEN)
app = Flask(W(109,97,115,104,105,110,107,97))
CHAT_ID = None
SYMBOLS = [W(66,84,67,85,83,68,84)]
SYMBOLS += [W(69,84,72,85,83,68,84)]
SYMBOLS += [W(83,79,76,85,83,68,84)]
SYMBOLS += [W(66,78,66,85,83,68,84)]
SYMBOLS += [W(88,82,80,85,83,68,84)]
SYMBOLS += [W(68,79,71,69,85,83,68,84)]
positions = {}
balance = 500.0
H = W(104,116,116,112,115,58,47,47)
T1 = W(116,101,115,116,110,101,116,46,98,105,110,97,110,99,101)
T2 = W(46,118,105,115,105,111,110)
B1X = W(97,112,105,46,98,105,110,97,110,99,101)
B2X = W(46,99,111,109)
BASE1 = H + T1 + T2
BASE2 = H + B1X + B2X
KLINE = W(47,97,112,105,47,118,51,47,107,108,105,110,101,115)
PRICE = W(47,97,112,105,47,118,51,47,116,105,99,107,101,114,47,112,114,105,99,101)
SP = chr(32)
NL = chr(10)
A1 = W(82,83,73,95,79,75)
A2 = W(82,83,73,95,78,79)
B1 = W(69,77,65,95,79,75)
B2 = W(69,77,65,95,78,79)
C1 = W(84,114,101,110,100,95,79,75)
C2 = W(84,114,101,110,100,95,78,79)
D1 = W(83,116,111,99,104,95,79,75)
D2 = W(83,116,111,99,104,95,78,79)
E1 = W(77,65,67,68,95,79,75)
E2 = W(77,65,67,68,95,78,79)
@app.route(W(47))
def home():
    return W(77,97,115,104,105,110,107,97,95,79,78)
def klines(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + KLINE
            p = {}
            p[W(115,121,109,98,111,108)] = s
            p[W(105,110,116,101,114,118,97,108)] = W(49,53,109)
            p[W(108,105,109,105,116)] = 100
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
def price(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + PRICE
            p = {}
            p[W(115,121,109,98,111,108)] = s
            r = requests.get(u, params=p, timeout=10)
            r = r.json()
            return float(r[W(112,114,105,99,101)])
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
    if op.lt(r, 50):
        score += 1
        det.append(A1)
    else:
        det.append(A2)
    if op.gt(p, e20):
        score += 1
        det.append(B1)
    else:
        det.append(B2)
    if op.gt(e20, e50):
        score += 1
        det.append(C1)
    else:
        det.append(C2)
    if op.lt(st, 50):
        score += 1
        det.append(D1)
    else:
        det.append(D2)
    if op.gt(m, 0):
        score += 1
        det.append(E1)
    else:
        det.append(E2)
    res = {}
    res[W(112,114,105,99,101)] = p
    res[W(114,115,105)] = r
    res[W(101,109,97,50,48)] = e20
    res[W(101,109,97,53,48)] = e50
    res[W(115,116,111,99,104)] = st
    res[W(109,97,99,100)] = m
    res[W(115,99,111,114,101)] = score
    res[W(100,101,116)] = det
    return res
def loop():
    global balance
    time.sleep(10)
    send(W(77,97,115,104,105,110,107,97,95,70,73,78,65,76,95,122,97,112,117,115,104,101,110,97))
    while True:
        try:
            for s in SYMBOLS:
                d = analyze(s)
                if not d:
                    continue
                p = d[W(112,114,105,99,101)]
                if s in positions:
                    en = positions[s][W(112,114,105,99,101)]
                    pnl = (p - en) / en * 100
                    if op.ge(pnl, 4):
                        del positions[s]
                        balance += 50 * pnl / 100
                        msg = W(80,82,79,68,65,90,72
