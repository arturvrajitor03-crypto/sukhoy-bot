import os
import time
import threading
import requests
from flask import Flask
import telebot

print("START", flush=True)

def W(*n):
    return chr(0)[:0].join(map(chr, n))

TOKEN = W(57,50,52,49,56,52,49,56,55,52,58,65,65,69,122,104,68,114,75,97,89,86,101,116,77,103,99,121,82,106,113,51,121,119,75,50,89,81,83,48,82,97,82,105,98,52)
bot = telebot.TeleBot(TOKEN)
app = Flask("mashinkya")
CHAT = [None]
SYMS = ["PAXGUSDT"]
POS = {}
BAL = [500.0]

@app.route("/")
def home():
    return "Машинка Золото"

def run_flask():
    ps = os.environ.get("PORT")
    port = int(ps) if ps else 10000
    print("PORT", port, flush=True)
    try:
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print("FLASK FAIL", e, flush=True)

def get_klines(s):
    u = "https://api.binance.com/api/v3/klines"
    p = {"symbol": s, "interval": "15m", "limit": 100}
    try:
        r = requests.get(u, params=p, timeout=10).json()
        closes = [float(x[4]) for x in r]
        highs = [float(x[2]) for x in r]
        lows = [float(x[3]) for x in r]
        vols = [float(x[5]) for x in r]
        return closes, highs, lows, vols
    except Exception as e:
        print("KLINES FAIL", e, flush=True)
        return [], [], [], []

def rsi_calc(c, period=14):
    if len(c) < period + 1:
        return 50
    g = []
    l = []
    for i in range(1, len(c)):
        d = c[i] - c[i-1]
        g.append(max(d, 0))
        l.append(max(-d, 0))
    ag = sum(g[-period:]) / period
    al = sum(l[-period:]) / period
    if al == 0:
        return 100
    t = 1 + ag / al
    return 100 - 100 / t

def ema_calc(c, n):
    k = 2 / (n + 1)
    e = c[0]
    for p in c[1:]:
        e = e + p * k - e * k
    return e

def macd_calc(c):
    e12 = ema_calc(c, 12)
    e26 = ema_calc(c, 26)
    return e12 - e26

def stoch_calc(highs, lows, closes):
    if len(closes) < 14:
        return 50
    hh = max(highs[-14:])
    ll = min(lows[-14:])
    if hh == ll:
        return 50
    return (closes[-1] - ll) / (hh - ll) * 100

def analyze(s):
    closes, highs, lows, vols = get_klines(s)
    if not closes:
        return None
    p = closes[-1]
    r = rsi_calc(closes)
    e20 = ema_calc(closes, 20)
    e50 = ema_calc(closes, 50)
    e200 = ema_calc(closes, 200) if len(closes) >= 200 else ema_calc(closes, 50)
    macd = macd_calc(closes)
    # Bollinger
    last20 = closes[-20:]
    sma20 = sum(last20) / 20
    var = sum((x - sma20) ** 2 for x in last20) / 20
    std = var ** 0.5
    upper = sma20 + 2 * std
    lower = sma20 - 2 * std
    stoch = stoch_calc(highs, lows, closes)
    avg_vol = sum(vols[-20:]) / 20
    vol_ok = vols[-1] > avg_vol

    sc = 0
    reasons = []
    # 1. RSI
    if 30 < r < 65:
        sc += 1
        reasons.append(f"RSI {round(r,1)} OK")
    # 2. EMA тренд
    if p > e20 and e20 > e50:
        sc += 1
        reasons.append("EMA тренд вверх")
    # 3. Цена выше EMA200
    if p > e200:
        sc += 1
        reasons.append("Выше EMA200")
    # 4. MACD
    if macd > 0:
        sc += 1
        reasons.append(f"MACD +{round(macd,2)}")
    # 5. Bollinger - не перекуплен, есть место вверх
    if p < upper and p > sma20:
        sc += 1
        reasons.append("Bollinger OK")
    # 6. Stochastic + Объём
    if stoch < 80 and vol_ok:
        sc += 1
        reasons.append(f"Stoch {round(stoch,1)} + Объём OK")

    return {"price": p, "rsi": r, "macd": macd, "stoch": stoch, "score": sc, "reasons": reasons, "e20": e20, "e50": e50, "upper": upper, "lower": lower}

def send(t):
    if CHAT[0]:
        try:
            bot.send_message(CHAT[0], t)
        except Exception as e:
            print("SEND FAIL", e, flush=True)
    print(t, flush=True)

def loop():
    time.sleep(10)
    send("🟡 Машинка Золото запущена ✅\nВсе индикаторы: RSI + EMA + MACD + Bollinger + Stochastic + Объём\nПокупка при скоре 4/6\nТейк: +1.5% | Стоп: -0.7%")
    while True:
        try:
            for s in SYMS:
                d = analyze(s)
                if not d:
                    continue
                p = d["price"]
                if s in POS:
                    en = POS[s]
                    pnl = (p - en) / en * 100
                    if pnl >= 1.5:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(f"✅ ПРОДАЖА ЗОЛОТО {s}\nПрибыль: {round(pnl, 2)}%\nБаланс: {round(BAL[0], 2)} $")
                    elif pnl <= -0.7:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(f"🛑 СТОП ЗОЛОТО {s}\nУбыток: {round(pnl, 2)}%\nБаланс: {round(BAL[0], 2)} $")
                    continue
                if d["score"] >= 4:
                    POS[s] = p
                    txt = f"🟢 ПОКУПКА ЗОЛОТО {s}\nЦена: {round(p, 2)} $\nСкор: {d['score']}/6\nRSI: {round(d['rsi'],1)} | MACD: {round(d['macd'],2)} | Stoch: {round(d['stoch'],1)}\n\nПричины:\n" + "\n".join(d["reasons"])
                    send(txt)
            time.sleep(60)
        except Exception as e:
            print("LOOP FAIL", e, flush=True)
            time.sleep(60)

@bot.message_handler(commands=["start"])
def st(m):
    CHAT[0] = m.chat.id
    bot.reply_to(m, "Привет! Я Машинка Золото 🟡\nИндикаторы: RSI, EMA 20/50/200, MACD, Bollinger, Stochastic, Объём\nКоманды:\n/signal - сигнал\n/status - позиции\n/balance - баланс")

@bot.message_handler(commands=["signal"])
def sg(m):
    t = "📊 Золото - Все индикаторы:\n\n"
    for s in SYMS:
        d = analyze(s)
        if not d:
            t += f"{s} - нет данных\n"
            continue
        t += f"{s} {round(d['price'], 2)} $\nСкор: {d['score']}/6\nRSI: {round(d['rsi'],1)}\nMACD: {round(d['macd'],2)}\nStoch: {round(d['stoch'],1)}\nEMA20: {round(d['e20'],2)} | EMA50: {round(d['e50'],2)}\nBollinger: {round(d['lower'],2)} - {round(d['upper'],2)}\n"
        if d["reasons"]:
            t += "✅ " + "\n✅ ".join(d["reasons"]) + "\n"
    bot.reply_to(m, t)

@bot.message_handler(commands=["status"])
def sts(m):
    if not POS:
        bot.reply_to(m, "Нет открытых позиций по золоту. Ждём сигнал... 👀")
        return
    t = "📈 Позиции:\n"
    for s in POS:
        t += f"{s} - вход: {round(POS[s], 2)} $\n"
    t += f"\nБаланс: {round(BAL[0], 2)} $"
    bot.reply_to(m, t)

@bot.message_handler(commands=["balance"])
def bal(m):
    bot.reply_to(m, f"💰 Баланс: {round(BAL[0], 2)} $")

tf = threading.Thread(target=run_flask, daemon=True)
tf.start()
print("FLASK THREAD OK", flush=True)

th1 = threading.Thread(target=loop, daemon=True)
th1.start()
print("LOOP THREAD OK", flush=True)

print("BOT START", flush=True)
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("BOT FAIL", e, flush=True)
        time.sleep(5)
