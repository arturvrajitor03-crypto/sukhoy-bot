import os, time, threading, requests
from flask import Flask
import pandas as pd
import numpy as np

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "BTCUSDT"
INTERVAL = "15m"
BALANCE = 500.0
POSITION = None
TRADES = 0
PNL = 0.0

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running - SMART v2"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(e)

def get_klines():
    url = "https://api.binance.com/api/v3/klines"
    r = requests.get(url, params={"symbol": SYMBOL, "interval": INTERVAL, "limit": 100}, timeout=10)
    data = r.json()
    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","q","n","tb","tq","x"])
    df["c"] = df["c"].astype(float)
    df["h"] = df["h"].astype(float)
    df["l"] = df["l"].astype(float)
    return df

def indicators(df):
    close = df["c"]
    # EMA 50 / 200 - ТРЕНД
    ema50 = close.ewm(span=50).mean().iloc[-1]
    ema200 = close.ewm(span=200).mean().iloc[-1]
    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_val = rsi.iloc[-1]
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    macd_val = macd.iloc[-1]
    signal_val = signal.iloc[-1]
    # Bollinger 20, 2
    sma20 = close.rolling(20).mean().iloc[-1]
    std20 = close.rolling(20).std().iloc[-1]
    upper = sma20 + 2*std20
    lower = sma20 - 2*std20
    # Ширина Bollinger - фильтр флэта
    width = (upper - lower) / sma20 * 100
    price = close.iloc[-1]
    return {
        "price": price, "ema50": ema50, "ema200": ema200,
        "rsi": rsi_val, "macd": macd_val, "signal": signal_val,
        "upper": upper, "lower": lower, "width": width
    }

def check_trade():
    global BALANCE, POSITION, TRADES, PNL
    df = get_klines()
    ind = indicators(df)
    price = ind["price"]

    # Если есть открытая позиция - проверяем TP / SL
    if POSITION:
        if POSITION["side"] == "BUY":
            if price >= POSITION["tp"]:
                profit = (POSITION["tp"] - POSITION["entry"]) * 0.05
                BALANCE += profit; PNL += profit; TRADES += 1
                send(f"✅ TP! BUY закрыта +{profit:.1f}$\nБаланс: {BALANCE:.1f}$ | Сделок: {TRADES} | PnL: {PNL:.1f}$")
                POSITION = None
            elif price <= POSITION["sl"]:
                loss = (POSITION["sl"] - POSITION["entry"]) * 0.05
                BALANCE += loss; PNL += loss; TRADES += 1
                send(f"❌ SL! BUY закрыта {loss:.1f}$\nБаланс: {BALANCE:.1f}$ | Сделок: {TRADES} | PnL: {PNL:.1f}$")
                POSITION = None
        else: # SELL
            if price <= POSITION["tp"]:
                profit = (POSITION["entry"] - POSITION["tp"]) * 0.05
                BALANCE += profit; PNL += profit; TRADES += 1
                send(f"✅ TP! SELL закрыта +{profit:.1f}$\nБаланс: {BALANCE:.1f}$ | Сделок: {TRADES} | PnL: {PNL:.1f}$")
                POSITION = None
            elif price >= POSITION["sl"]:
                loss = (POSITION["entry"] - POSITION["sl"]) * 0.05
                BALANCE += loss; PNL += loss; TRADES += 1
                send(f"❌ SL! SELL закрыта {loss:.1f}$\nБаланс: {BALANCE:.1f}$ | Сделок: {TRADES} | PnL: {PNL:.1f}$")
                POSITION = None
        return

    # Нет позиции - ищем сигнал, но ТОЛЬКО если все фильтры совпали
    # Фильтр флэта: если Bollinger узкий < 0.8% - рынок спит, не торгуем
    if ind["width"] < 0.8:
        print(f"Флэт, ширина {ind['width']:.2f}% - пропускаю")
        return

    # SELL: Тренд вниз + RSI высокий + MACD вниз + цена у верхней границы
    if ind["ema50"] < ind["ema200"] and ind["rsi"] > 60 and ind["macd"] < ind["signal"] and price > ind["upper"] - 100:
        entry = price
        tp = entry - 900
        sl = entry + 600
        POSITION = {"side": "SELL", "entry": entry, "tp": tp, "sl": sl}
        send(f"🔴 SMART SELL BTC\nВход: {entry:.0f}\nTP: {tp:.0f} (+45$)\nSL: {sl:.0f} (-30$)\nRSI: {ind['rsi']:.1f} | EMA50<{ind['ema50']:.0f} < EMA200 {ind['ema200']:.0f}\nMACD подтверждает | Bollinger: у верха")
        return

    # BUY: Тренд вверх + RSI низкий + MACD вверх + цена у нижней границы
    if ind["ema50"] > ind["ema200"] and ind["rsi"] < 40 and ind["macd"] > ind["signal"] and price < ind["lower"] + 100:
        entry = price
        tp = entry + 900
        sl = entry - 600
        POSITION = {"side": "BUY", "entry": entry, "tp": tp, "sl": sl}
        send(f"🟢 SMART BUY BTC\nВход: {entry:.0f}\nTP: {tp:.0f} (+45$)\nSL: {sl:.0f} (-30$)\nRSI: {ind['rsi']:.1f} | EMA50 {ind['ema50']:.0f} > EMA200 {ind['ema200']:.0f}\nMACD подтверждает | Bollinger: у низа")
        return

    print(f"Нет сигнала. Цена {price:.0f} RSI {ind['rsi']:.1f} Width {ind['width']:.2f}%")

def loop():
    while True:
        try:
            check_trade()
        except Exception as e:
            print("Ошибка:", e)
        time.sleep(300) # 5 минут

def telegram_poll():
    offset = 0
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={"offset": offset, "timeout": 20}, timeout=30).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                txt = u.get("message", {}).get("text", "")
                if txt == "/balance":
                    send(f"💰 Баланс: {BALANCE:.1f}$\nСделок: {TRADES}\nPnL: {PNL:.1f}$\nОткрытая: {POSITION if POSITION else 'нет'}")
                if txt == "/start":
                    send("🤖 SMART Bot v2 работает! EMA + RSI + MACD + Bollinger + Фильтр флэта")
        except Exception as e:
            print(e)
            time.sleep(5)

threading.Thread(target=loop, daemon=True).start()
threading.Thread(target=telegram_poll, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
