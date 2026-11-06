import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")

BALANCE = 1000.0
price_history = deque(maxlen=50)
open_trades = []

def get_gold_price():
    headers={'User-Agent':'Mozilla/5.0'}
    try:
        r=requests.get("https://api.gold-api.com/price/XAU",headers=headers,timeout=5).json()
        p=float(r.get('price',0))
        if p>3000: return p
    except: pass
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT",timeout=5).json()
        return float(r['result']['list'][0]['lastPrice'])
    except: pass
    return 4042.8

def get_rsi(prices, period=14):
    if len(prices)<period+1: return 50
    gains=losses=0
    for i in range(1,period+1):
        diff=prices[-i]-prices[-i-1]
        if diff>0: gains+=diff
        else: losses+= -diff
    if losses==0: return 75
    rs=gains/losses if losses!=0 else 10
    return 100 - (100/(1+rs))

def get_signal
