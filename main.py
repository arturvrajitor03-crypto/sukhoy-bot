import os, time, threading, requests, math
from flask import Flask
import telebot
from binance.client import Client

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4")
CHAT_ID = None  # узнаем при /start

BINANCE_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_SECRET = os.environ.get("BINANCE_API_SECRET", "")
TRADE_AMOUNT_USDT = 50.0  # 50$ на сделку = 10% от 500$
STOP_LOSS_PCT = -2.5
TAKE_PROFIT_PCT = 4.0

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]

# --- TELEGRAM + FLASK (чтобы Render не спал) ---
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive! Trading mode ON"

# --- BINANCE ---
binance = None
PAPER_MODE = True
if BINANCE_KEY and BINANCE_SECRET:
    try:
        binance = Client(BINANCE_KEY, BINANCE_SECRET, testnet=True)
        PAPER_MODE = False
        print("Binance Testnet connected")
    except Exception as e:
        print("Binance error, paper mode:", e)

# Храним открытые позиции: { "BTCUSDT": {"price": 97000, "qty": 0.0005} }
positions = {}
balance_paper = 500.0

def get_klines(symbol, limit=100):
    try:
        url = f"https://testnet.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit={limit}"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        return closes
    except:
        return []

def calc_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(closes, period=50):
    if len(closes) < period: return closes[-1]
    k = 2 / (period + 1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def get_price(symbol):
    try:
        url = f"https://testnet.binance.vision/api/v3/ticker/price?symbol={symbol}"
        return float(requests.get(url, timeout=10).json()['price'])
    except:
        return None

def send_msg(text):
    global CHAT_ID
    if CHAT_ID:
        try: bot.send_message(CHAT_ID, text)
        except: pass
    print(text)

def trading_loop():
    global balance_paper
    time.sleep(10)
    send_msg("🤖 Авто-трейдинг запущен!\nДепозит: 500$ (Testnet / Бумага)\nСделка: 50$\nМонеты: BTC ETH SOL BNB XRP DOGE")
    while True:
        try:
            for symbol in SYMBOLS:
                closes = get_klines(symbol)
                if not closes: continue
                price = closes[-1]
                rsi = calc_rsi(closes)
                ema = calc_ema(closes)

                # --- ПРОВЕРКА ВЫХОДА ---
                if symbol in positions:
                    entry = positions[symbol]['price']
                    pnl_pct = (price - entry) / entry * 100
                    if pnl_pct >= TAKE_PROFIT_PCT:
                        qty = positions[symbol]['qty']
                        del positions[symbol]
                        send_msg(f"✅ ПРОДАЖА {symbol}\nПрибыль: +{pnl_pct:.2f}%\nЦена: {price}\n+{TRADE_AMOUNT_USDT * pnl_pct/100:.2f}$")
                        if not PAPER_MODE and binance:
                            try: binance.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                            except Exception as e: print(e)
                        else:
                            balance_paper += TRADE_AMOUNT_USDT * pnl_pct/100
                    elif pnl_pct <= STOP_LOSS_PCT:
                        qty = positions[symbol]['qty']
                        del positions[symbol]
                        send_msg(f"🛑 СТОП-ЛОСС {symbol}\nУбыток: {pnl_pct:.2f}%\nЦена: {price}")
                        if not PAPER_MODE and binance:
                            try: binance.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                            except Exception as e: print(e)
                        else:
                            balance_paper += TRADE_AMOUNT_USDT * pnl_pct/100
                    continue

                # --- ПРОВЕРКА ВХОДА: RSI < 35 и цена > EMA50 ---
                if rsi < 35 and price > ema:
                    qty = TRADE_AMOUNT_USDT / price
                    # округление под Binance
                    qty = math.floor(qty * 100000) / 100000
                    positions[symbol] = {"price": price, "qty": qty}
                    send_msg(f"🟢 ПОКУПКА {symbol}\nЦена: {price}\nRSI: {rsi:.1f} (дешево)\nСумма: {TRADE_AMOUNT_USDT}$\nСтоп: -2.5% / Тейк: +4%")
                    if not PAPER_MODE and binance:
                        try: binance.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        except Exception as e:
                            print(e)
                            del positions[symbol]
            time.sleep(60)  # проверка каждую минуту
        except Exception as e:
            print("Loop error:", e)
            time.sleep(60)

# --- КОМАНДЫ ---
@bot.message_handler(commands=['start'])
def start(m):
    global CHAT_ID
    CHAT_ID = m.chat.id
    bot.reply_to(m, f"🤖 Бот работает!\nРежим: {'🧪 ТЕСТ (бумага)' if PAPER_MODE else '🟡 TESTNET Binance'}\nДепозит: 500$\nКоманды:\n/status - позиции\n/balance - баланс\n/all - цены")

@bot.message_handler(commands=['status'])
def status(m):
    if not positions:
        bot.reply_to(m, "Нет открытых позиций. Ждём сигнал...")
        return
    txt = "📊 Открытые позиции:\n"
    for s, p in positions.items():
        cur = get_price(s)
        pnl = (cur - p['price'])/p['price']*100 if cur else 0
        txt += f"{s}: {pnl:.2f}% (вход {p['price']})\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['balance'])
def bal(m):
    bot.reply_to(m, f"💰 Баланс (бумага): {balance_paper:.2f}$\nОткрыто позиций: {len(positions)}")

@bot.message_handler(commands=['all'])
def all_prices(m):
    txt = "💲 Цены:\n"
    for s in SYMBOLS:
        p = get_price(s)
        txt += f"{s}: {p}\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['btc'])
def btc(m):
    bot.reply_to(m, f"BTC: {get_price('BTCUSDT')}$")

# --- ЗАПУСК ---
threading.Thread(target=trading_loop, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
