import os
import time
import threading
import requests
import math
import operator as op
from flask import Flask
import telebot

# VSE SLOVA TUT - BEZ PROBELOV
A1 = 'RSI_OK'
A2 = 'RSI_NO'
B1 = 'EMA_OK'
B2 = 'EMA_NO'
C1 = 'Trend_OK'
C2 = 'Trend_NO'
D1 = 'Stoch_OK'
D2 = 'Stoch_NO'
E1 = 'MACD_OK'
E2 = 'MACD_NO'
SP = chr(32)
NL = chr(10)
TOKEN = '9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4'
bot = telebot.TeleBot(TOKEN)
app = Flask('mashinka')
CHAT_ID = None
SYMBOLS = ['BTCUSDT']
SYMBOLS += ['ETHUSDT']
SYMBOLS += ['SOLUSDT']
SYMBOLS += ['BNBUSDT']
SYMBOLS += ['XRPUSDT']
SYMBOLS += ['DOGEUSDT']
positions = {}
balance = 500.0
H = 'https://'
T1 = 'testnet.binance'
T2 = '.vision'
B1X = 'api.binance'
B2X = '.com'
BASE1 = H + T1 + T2
BASE2 = H + B1X + B2X
KLINE = '/api/v3/klines'
PRICE = '/api/v3/ticker/price'

@app.route('/')
def home():
    return 'Mashinka_ON'

def klines(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + KLINE
            p = {}
            p['symbol'] = s
            p['interval'] = '15m'
            p['limit'] = 100
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
            p['symbol'] = s
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
    res['price'] = p
    res['rsi'] = r
    res['ema20'] = e20
    res['ema50'] = e50
    res['stoch'] = st
    res['macd'] = m
    res['score'] = score
    res['det'] = det
    return res

def loop():
    global balance
    time.sleep(10)
    msg0 = 'Mashinka_FINAL_zapushena'
    send(msg0)
    while True:
        try:
            for s in SYMBOLS:
                d = analyze(s)
                if not d:
                    continue
                p = d['price']
                if s in positions:
                    en = positions[s]['price']
                    pnl = (p - en) / en * 100
                    if op.ge(pnl, 4):
                        del positions[s]
                        balance += 50 * pnl / 100
                        msg = 'PRODAZHA'
                        msg += SP
                        msg += s
                        send(msg)
                    elif op.le(pnl, -2.5):
                        del positions[s]
                        balance += 50 * pnl / 100
                        msg = 'STOP'
                        msg += SP
                        msg += s
                        send(msg)
                    continue
                if op.ge(d['score'], 3):
                    q = math.floor((50 / p) * 100000)
                    q = q / 100000
                    positions[s] = {}
                    positions[s]['price'] = p
                    positions[s]['qty'] = q
                    msg = 'POKUPKA'
                    msg += SP
                    msg += s
                    msg += SP
                    msg += str(round(p, 2))
                    send(msg)
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(60)

@bot.message_handler(commands=['start'])
def st(m):
    global CHAT_ID
    CHAT_ID = m.chat.id
    txt = 'Mashinka_FINAL_rabotaet'
    bot.reply_to(m, txt)

@bot.message_handler(commands=['status'])
def st2(m):
    if not positions:
        bot.reply_to(m, 'Net_pozicij')
        return
    t = 'Pozicii'
    t += NL
    for s, v in positions.items():
        cur = price(s)
        pnl = 0
        if cur:
            pnl = (cur - v['price']) / v['price'] * 100
        t += s
        t += SP
        t += str(round(pnl, 2))
        t += NL
    bot.reply_to(m, t)

@bot.message_handler(commands=['signal'])
def sg(m):
    t = 'Signaly'
    t += NL
    t += NL
    for s in SYMBOLS:
        d = analyze(s)
        if not d:
            t += s
            t += SP
            t += '
