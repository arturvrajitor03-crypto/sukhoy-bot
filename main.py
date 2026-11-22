import os, time, threading, requests, math
from flask import Flask
import telebot
from binance.client import Client

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
    return "Bot v3 alive!"

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
        url = "https://testnet.binance.vision/api/v3/klines"
        params = {"symbol": symbol, "interval": "15m", "limit": limit}
        r = requests.get(url, params=params, timeout=10).json()
        closes = [float(x[4]) for x in r]
        return closes
    except:
        return []

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0:
        return 100
    rs = ag / al
    return 100 - (100 / (1 + rs))

def calc_ema_list(closes, period):
    k = 2 / (period + 1)
    ema = closes[0]
    out = [ema]
    for p in closes[1:]:
        ema = p * k + ema * (1 - k)
        out.append(ema)
    return out

def calc_ema(closes, period):
    lst = calc_ema_list(closes, period)
    return lst[-1]

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0
    ema12 = calc_ema_list(closes, 12)
    ema26 = calc_ema_list(closes, 26)
    macd_line = []
    for a, b in zip(ema12, ema26):
        macd_line.append(a - b)
    sig_list = calc_ema_list(macd_line, 9)
    return macd_line[-1], sig_list[-1]

def calc_bollinger(closes, period=20):
    if len(closes) < period:
        return closes[-1], closes[-1], closes[-1]
    ma = sum(closes[-period:]) / period
    s = 0
    for x in closes[-period:]:
        s += (x - ma) ** 2
    std = (s / period) ** 0.5
    upper = ma + 2 * std
    lower = ma - 2 * std
    return upper, ma, lower

def calc_stoch(closes, period=14):
    if len(closes) < period:
        return 50
    low = min(closes[-period:])
    high = max(closes[-period:])
    if high == low:
        return 50
    return (closes[-1] - low) / (high - low) * 100

def get_price(symbol):
    try:
        url = "https://testnet.binance.vision/api/v3/ticker/price"
        r = requests.get(url, params={"symbol": symbol}, timeout=10).json()
        return float(r['price'])
    except:
        return None

def send_msg(text):
    global CHAT_ID
    if CHAT_ID:
        try:
            bot.send_message(CHAT_ID, text)
        except:
            pass
    print(text)

def analyze(symbol):
    closes = get_klines(symbol)
    if not closes:
        return None
    price = closes[-1]
    rsi = calc_rsi(closes)
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    macd, signal = calc_macd(closes)
    upper, mid, lower = calc_bollinger(closes)
    stoch = calc_stoch(closes)
    score = 0
    reasons = []
    if rsi < 45:
        score += 1
        reasons.append("RSI OK")
    else:
        reasons.append("RSI NO")
    if price > ema20:
        score += 1
        reasons.append("EMA20 OK")
    else:
        reasons.append("EMA20 NO")
    if ema20 > ema50:
        score += 1
        reasons.append("Trend OK")
    else:
        reasons.append("Trend NO")
    if macd > signal:
        score += 1
        reasons.append("MACD OK")
    else:
        reasons.append("MACD NO")
    if price < mid or stoch < 30:
        score += 1
        reasons.append("Boll OK")
    else:
        reasons.append("Boll NO")
    result = {}
    result["price"] = price
    result["rsi"] = rsi
    result["ema20"] = ema20
    result["ema50"] = ema50
    result["macd"] = macd
    result["signal"] = signal
    result["upper"] = upper
    result["lower"] = lower
    result["stoch"] = stoch
    result["score"] = score
    result["reasons"] = reasons
    return result

def trading_loop():
    global balance_paper
    time.sleep(10)
    send_msg("Bot v3 FIXED started! Multi-indicator ON")
    while True:
        try:
            for symbol in SYMBOLS:
                data = analyze(symbol)
                if not data:
                    continue
                price = data["price"]
                if symbol in positions:
                    entry = positions[symbol]["price"]
                    pnl = (price - entry) / entry * 100
                    if pnl >= TAKE_PROFIT_PCT:
                        qty = positions[symbol]["qty"]
                        del positions[symbol]
                        msg = "SELL " + symbol + " +" + str(round(pnl, 2)) + "%"
                        send_msg(msg)
                        if not PAPER_MODE and binance:
                            try:
                                binance.create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
                            except Exception as e:
                                print(e)
                        else:
                            balance_paper += TRADE_AMOUNT_USDT * pnl / 100
                    elif pnl <= STOP_LOSS_PCT:
                        qty = positions[symbol]["qty"]
                        del positions[symbol]
                        msg = "STOP " + symbol + " " + str(round(pnl, 2)) + "%"
                        send_msg(msg)
                        if not PAPER_MODE and binance:
                            try:
                                binance.create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
                            except Exception as e:
                                print(e)
                        else:
                            balance_paper += TRADE_AMOUNT_USDT * pnl / 100
                    continue
                if data["score"] >= 3:
                    qty = math.floor((TRADE_AMOUNT_USDT / price) * 100000) / 100000
                    positions[symbol] = {"price": price, "qty": qty}
                    r = " | ".join(data["reasons"])
                    msg = "BUY " + symbol + " Price " + str(round(price, 2)) + " Score " + str(data["score"]) + "/5 " + r
                    send_msg(msg)
                    if not PAPER_MODE and binance:
                        try:
                            binance.create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)
                        except Exception as e:
                            print(e)
                            del positions[symbol]
            time.sleep(60)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(60)

@bot.message_handler(commands=['start'])
def start(m):
    global CHAT_ID
    CHAT_ID = m.chat.id
    bot.reply_to(m, "Bot v3 FIXED works! Commands: /status /signal /balance /all")

@bot.message_handler(commands=['status'])
def status(m):
    if not positions:
        bot.reply_to(m, "No open positions. Waiting...")
        return
    txt = "Positions:\n"
    for s, p in positions.items():
        cur = get_price(s)
        pnl = (cur - p["price"]) / p["price"] * 100 if cur else 0
        txt += s + ": " + str(round(pnl, 2)) + "%\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['signal'])
def signal(m):
    txt = "Indicators:\n\n"
    for s in SYMBOLS:
        d = analyze(s)
        if not d:
            continue
        txt += s + " " + str(round(d["price"], 2)) + " Score " + str(d["score"]) + "/5\n"
        txt += "RSI " + str(round(d["rsi"], 1)) + " Stoch " + str(round(d["stoch"], 1)) + "\n"
        txt += "EMA20 " + str(round(d["ema20"], 2)) + " EMA50 " + str(round(d["ema50"], 2)) + "\n"
        txt += "MACD " + str(round(d["macd"], 2)) + " vs " + str(round(d["signal"], 2)) + "\n"
        txt += "Boll " + str(round(d["lower"], 2)) + " - " + str(round(d["upper"], 2)) + "\n"
        txt += " | ".join(d["reasons"]) + "\n\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['balance'])
def bal(m):
    bot.reply_to(m, "Balance: " + str(round(balance_paper, 2)) + "$ Positions: " + str(len(positions)))

@bot.message_handler(commands=['all'])
def all_p(m):
    txt = "Prices:\n"
    for s in SYMBOLS:
        txt += s + ": " + str(get_price(s)) + "\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['btc'])
def btc(m):
    bot.reply_to(m, "BTC: " + str(get_price("BTCUSDT")) + "$")

threading.Thread(target=trading_loop, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
