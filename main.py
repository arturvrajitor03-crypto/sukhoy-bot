import os
import sys
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
app = Flask(W(109,97,115,104,105,110,107,97))
CHAT = [None]
S1 = W(66,84,67,85,83,68,84)
S2 = W(69,84,72,85,83,68,84)
S3 = W(83,79,76,85,83,68,84)
SYMS = [S1, S2, S3]
POS = {}
BAL = [500.0]
@app.route(W(47))
def home():
    return W(77,97)
def klines(s):
    u = W(104,116,116,112,115,58,47,47)
    u += W(97,112,105,46,98,105,110,97,110,99,101,46,99,111,109)
    u += W(47,97,112,105,47,118,51,47,107,108,105,110,101,115)
    p = {}
    p[W(115,121,109,98,111,108)] = s
    p[W(105,110,116,101,114,118,97,108)] = W(49,53,109)
    p[W(108,105,109,105,116)] = 100
    try:
        r = requests.get(u, params=p, timeout=10)
        r = r.json()
        out = []
        for x in r:
            out.append(float(x[4]))
        return out
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
    t = 1 + ag / al
    return 100 - 100 / t
def ema(c, n):
    t = n + 1
    k = 2 / t
    e = c[0]
    for p in c[1:]:
        e = p * k + e * (1 - k)
    return e
def analyze(s):
    c = klines(s)
    if not c:
        return None
    p = c[-1]
    r = rsi(c)
    e20 = ema(c, 20)
    e50 = ema(c, 50)
    sc = 0
    if r < 50:
        sc += 1
    if p > e20:
        sc += 1
    if e20 > e50:
        sc += 1
    return [p, r, sc]
def send(t):
    if CHAT[0]:
        try:
            bot.send_message(CHAT[0], t)
        except Exception as e:
            print("SEND FAIL", e, flush=True)
    print(t, flush=True)
def loop():
    time.sleep(10)
    send(W(77,97,115,104,105,110,107,97))
    while True:
        try:
            for s in SYMS:
                d = analyze(s)
                if not d:
                    continue
                p = d[0]
                if s in POS:
                    en = POS[s]
                    pnl = (p - en) / en * 100
                    if pnl >= 4:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(W(80,82,79,68,65,90,72,65) + chr(32) + s)
                    elif pnl <= -2.5:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(W(83,84,79,80) + chr(32) + s)
                    continue
                if d[2] >= 2:
                    POS[s] = p
                    send(W(80,79,75,85,80,75,65) + chr(32) + s + chr(32) + str(round(p, 2)))
            time.sleep(60)
        except Exception as e:
            print("LOOP FAIL", e, flush=True)
            time.sleep(60)
@bot.message_handler(commands=[W(115,116,97,114,116)])
def st(m):
    CHAT[0] = m.chat.id
    bot.reply_to(m, W(77,97,115,104,105,110,107,97))
@bot.message_handler(commands=[W(115,105,103,110,97,108)])
def sg(m):
    t = W(83,105,103,110,97,108,121) + chr(10) + chr(10)
    for s in SYMS:
        d = analyze(s)
        if not d:
            t += s + chr(32) + W(110,101,116) + chr(10)
            continue
        t += s + chr(32) + str(round(d[0], 2))
        t += chr(32) + W(83,107,111,114) + chr(32) + str(d[2]) + chr(10)
    bot.reply_to(m, t)
th1 = threading.Thread(target=loop)
th1.daemon = True
th1.start()
print("THREAD1 OK", flush=True)
th2 = threading.Thread(target=bot.infinity_polling)
th2.daemon = True
th2.start()
print("THREAD2 OK", flush=True)
ps = os.environ.get(W(80,79,82,84))
if ps:
    port = int(ps)
else:
    port = 10000
print("PORT", port, flush=True)
try:
    app.run(host=W(48,46,48,46,48,46,48), port=port)
except Exception as e:
    print("APP RUN FAIL", e, flush=True)
    raise
