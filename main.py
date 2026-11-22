import os
import time
import threading
import traceback
from flask import Flask
from flask import request
import telebot
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
APP_URL = APP_URL.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

BAL = 500.0
POS = None
HIST = []
LAST_TRADE = 0

def get_data():
    import yfinance as yf
    d15 = yf.download("BTC-USD", period="5d", interval="15m", progress=False, auto_adjust=False)
    if d15.columns.nlevels > 1:
        d15.columns = d15.columns.get_level_values(0)
    d15 = d15.dropna()
    d1h = yf.download("BTC-USD", period="1mo", interval="1h", progress=False, auto_adjust=False)
    if d1h.columns.nlevels > 1:
        d1h.columns = d1h.columns.get_level_values(0)
    d1h = d1h.dropna()
    s = pd.Series(d15["Close"].values.flatten())
    s1h = pd.Series(d1h["Close"].values.flatten())
    price = float(s.iloc[-1])
    ema50 = float(s.ewm(span=50).mean().iloc[-1])
    e200 = float(s1h.ewm(span=200).mean().iloc[-1])
    if price > e200:
        trend = "UP"
    else:
        trend = "DOWN"
    delta = s.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    g = float(np.array(gain).flatten()[-1])
    l = float(np.array(loss).flatten()[-1])
    if l != 0:
        rsi = float(100 - (100 / (1 + g / l)))
    else:
        rsi = 50.0
    e12 = s.ewm(span=12).mean()
    e26 = s.ewm(span=26).mean()
    macd = e12 - e26
   
