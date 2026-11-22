import os
import time
import threading
import traceback
from io import BytesIO
from flask import Flask
from flask import request
import telebot
import pandas as pd
import numpy as np

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123456:ABC"
APP_URL = os.environ.get(
"RENDER_EXTERNAL_URL", "")
APP_URL = APP_URL.rstrip("/")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

BAL = 500.0
POS = None
HIST = []
LAST_TRADE = 0

def get_data():
    import yfinance as yf
    d15 = yf.download(
    "BTC-USD",
    period="5d",
    interval="15m",
    progress=False,
    auto_adjust=False)
    c = d15.columns
    if c.nlevels > 1:
        d15.columns = c.get_level_values(0)
    d15 = d15.dropna()
    d1h = yf.download(
    "BTC-USD",
    period="1mo",
    interval="1h",
    progress=False,
    auto_adjust=False)
    c2 = d1h.columns
    if c2.nlevels > 1:
        d1h.columns = c2.get_level_values(0)
    d1h = d1h.dropna()
    s = pd.Series(
    d15["Close"].values.flatten())
    s1h = pd.Series(
    d1h["Close"].values.flatten())
    price = float(s.iloc[-1])
    ema50 = float(
    s.ewm(span=50).mean().iloc[-1])
    e200 = float(
    s1h.ewm(span=200).mean().iloc[-1])
    if price > e200:
        trend = "UP"
    else:
        trend = "DOWN"
    delta = s.diff()
    gain = delta.where(delta > 0, 0)
    gain = gain.rolling(14).mean()
    loss = -delta.where(delta < 0
