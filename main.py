import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque
import math

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")

BALANCE = 1000.0
price_history = deque(maxlen=100)
open_trades = []
last_signal_time = 0

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
    try:
        r=requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT",timeout=5).json()
        return float(r['price'])
    except: pass
    return 4042.8

def get_prices_binance(limit=50):
    try:
        r=requests.get(f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit={limit}",timeout=5).json()
        closes=[float(x[4]) for x in r]
        return closes
    except: 
        return list(price_history) if len(price_history)>20 else [4040+i*0.5 for i in range(50)]

def calc_rsi(prices, period=14):
    if len(prices)<period+1: return 50
    gains=losses=0
    for i in range(1,period+1):
        diff=prices[-i]-prices[-i-1]
        if diff>0: gains+=diff
        else: losses+= -diff
    if losses==0: return 85
    rs=gains/max(losses,0.01)
    return 100 - (100/(1+rs))

def calc_ema(prices, period):
    if len(prices)<period: return prices[-1]
    k=2/(period+1)
    ema=prices[0]
    for p in prices[1:]: ema=p*k+ema*(1-k)
    return ema

def calc_macd(prices):
    if len(prices)<26: return 0,0
    ema12=calc_ema(prices,12)
    ema26=calc_ema(prices,26)
    macd=ema12-ema26
    signal=calc_ema(prices[-9:],9) if len(prices)>=9 else macd
    return macd, signal

def analyze_market():
    prices=get_prices_binance(50)
    if len(price_history)>5: prices=list(price_history)[-50:]
    
    p=prices[-1]
    rsi=calc_rsi(prices,14)
    ema20=calc_ema(prices,20)
    ema50=calc_ema(prices,50)
    macd, macd_sig=calc_macd(prices)
    
    # Bollinger
    sma20=sum(prices[-20:])/20 if len(prices)>=20 else p
    std=math.sqrt(sum((x-sma20)**2 for x in prices[-20:])/20) if len
