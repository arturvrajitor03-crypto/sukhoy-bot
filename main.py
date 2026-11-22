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
TOKEN = os.environ.get(
W(
84,
79,
75,
69,
78
)
)
if not TOKEN:
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
A = W(
109,
97,
115,
104,
105,
110,
107,
97
)
app = Flask(A)
CHAT = [None]
S1 = W(
66,
84,
67,
85,
83,
68,
84
)
S2 = W(
69,
84,
72,
85,
83,
68,
84
)
S3 = W(
83,
79,
76,
85,
83,
68,
84
)
SYMBOLS = [S1]
SYMBOLS += [S2]
SYMBOLS += [S3]
positions = {}
balance = 500.0
H = W(
104,
116,
116,
112,
115,
58,
47,
47
)
T1 = W(
116,
101,
115,
116,
110,
101,
116,
46,
98,
105,
110,
97,
110,
99,
101
)
T2 = W(
46,
118,
105,
115,
105,
111,
110
)
B1X = W(
97,
112,
105,
46,
98,
105,
110,
97,
110,
99,
101
)
B2X = W(
46,
99,
111,
109
)
BASE1 = H + T1 + T2
BASE2 = H + B1X + B2X
K1 = W(
47,
97,
112,
105,
47,
118,
51
)
K2 = W(
47,
107,
108,
105,
110,
101,
115
)
KLINE = K1 + K2
P1 = W(
47,
97,
112,
105,
47,
118,
51
)
P2 = W(
47,
116,
105,
99,
107,
101,
114
)
P3 = W(
47,
112,
114,
105,
99,
101
)
PRICE = P1 + P2 + P3
SP = chr(32)
NL = chr(10)
SYM = W(
115,
121,
109,
98,
111,
108
)
INT = W(
105,
110,
116,
101,
114,
118,
97,
108
)
LIM = W(
108,
105,
109,
105,
116
)
PRC = W(
112,
114,
105,
99,
101
)
RSI = W(
114,
115,
105
)
SCR = W(
115,
99,
111,
114,
101
)
QTY = W(
113,
116,
121
)
@app.route(W(47))
def home():
    return W(
77,
97
)
def klines(s):
    for base in [BASE1, BASE2]:
        try:
            u = base + KLINE
            p = {}
            p[SYM] = s
            p[INT] = W(
49,
53,
109
)
            p[LIM] = 100
            r = requests.get(
u,
params=p,
timeout=10
)
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
    k = 2 / (n +
