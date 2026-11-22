import os, time, threading, requests, math
from flask import Flask
import telebot
from binance.client import Client

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4")
CHAT_ID = None
BINANCE_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_SECRET = os.environ.get("BINANCE_API_SECRET", "")
TRADE_AMOUNT_USDT = 50.0
STOP_LOSS_PCT = -2.5
TAKE_PROFIT_PCT = 4.0
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot v3 MULTI-INDICATOR alive!"

binance = None
PAPER_MODE = True
if BINANCE_KEY and BINANCE_SECRET:
    try:
        binance = Client(BINANCE_KEY, BINANCE_SECRET, testnet=True)
        PAPER_MODE = False
    except Exception as e:
        print("Binance error:", e)

positions = {}
balance_paper = 500.0

def get_klines(symbol, limit=100):
    try:
        url = f"https://testnet.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit={limit}"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        volumes = [float(x[5]) for x in r]
        return closes, volumes
    except:
        return [], []

def calc_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag = sum(gains[-period:])/period; al = sum(losses[-period:])/period
    if al == 0: return 100
    rs = ag/al
    return 100 - (100/(1+rs))

def calc_ema_list(closes, period):
    k = 2/(period+1)
    ema = closes[0]
    out = [ema]
    for p in closes[1:]:
        ema = p*k + ema*(1-k)
        out.append(ema)
    return out

def calc_ema(closes, period):
    return calc_ema_list(closes, period)[-1]

def calc_macd(closes):
    if len(closes) < 26: return 0, 0
    ema12 = calc_ema_list(closes, 12)
    ema26 = calc_ema_list(closes, 26)
    macd_line = [a-b for a,b in zip(ema12, ema26)]
    signal = calc_ema_list(macd_line, 9)[-1]
    return macd_line[-1], signal

def calc_bollinger(closes, period=20):
    if len(closes) < period: return closes[-1], closes[-1], closes[-1]
    ma = sum(closes[-period:])/period
    std = (sum((x-ma)**2 for x in closes[-period:])/period)**0.5
    return ma + 2*std, ma, ma - 2*std

def calc_stoch(closes, period=14):
    if len(closes) < period: return 50
    low = min(closes[-period:]); high = max(closes[-period:])
    if high == low: return 50
    return (closes[-1]-low)/(high-low)*100

def get_price(symbol):
    try:
        url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
        return float(requests.get(url, timeout=10).json()['price'])
    except: return None

def send_msg(text):
    global CHAT_ID
    if CHAT_ID:
        try: bot.send_message(CHAT_ID, text)
        except: pass
    print(text)

def analyze(symbol):
    closes, volumes = get_klines(symbol)
    if not closes: return None
    price = closes[-1]
    rsi = calc_rsi(closes)
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    macd, signal = calc_macd(closes)
    upper, mid, lower = calc_bollinger(closes)
    stoch = calc_stoch(closes)
    # Голосование 5 индикаторов
    score = 0
    reasons = []
    if rsi < 45: score+=1; reasons.append(f"RSI {rsi:.0f}✅")
    else: reasons.append(f"RSI {rsi:.0f}❌")
    if price > ema20: score+=1; reasons.append("EMA20✅")
    else: reasons.append("EMA20❌")
    if ema20 > ema50: score+=1; reasons.append("Тренд✅")
    else: reasons.append("Тренд❌")
    if macd > signal: score+=1; reasons.append("MACD✅")
    else: reasons.append("MACD❌")
    if price < mid or stoch < 30: score+=1; reasons.append(f"Boll/Stoch✅")
    else: reasons.append("Boll/Stoch❌")
    return {"price":price,"rsi":rsi,"ema20":ema20,"ema50":ema50,"macd":macd,"signal":signal,"upper":upper,"
