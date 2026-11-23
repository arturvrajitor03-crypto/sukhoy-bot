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
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
POS = {}
BAL = [500.0]

@app.route("/")
def home():
    return "Машинка"

def run_flask():
    ps = os.environ.get("PORT")
    port = int(ps) if ps else 10000
    print("PORT", port, flush=True)
    try:
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print("FLASK FAIL", e, flush=True)

def klines(s):
    u = "https://api.binance.com/api/v3/klines"
    p = {"symbol": s, "interval": "15m", "limit": 100}
    try:
        r = requests.get(u, params=p, timeout=10).json()
        return [float(x[4]) for x in r]
    except Exception as e:
        print("KLINES FAIL", e, flush=True)
        return []

def rsi(c):
    if len(c) < 15:
        return 50
    g = []
    l = []
    for i in range(1, len(c)):
        d = c[i] - c[i-1]
        g.append(max(d, 0))
        l.append(max(-d, 0))
    ag = sum(g[-14:]) / 14
    al = sum(l[-14:]) / 14
    if al == 0:
        return 100
    t = 1 + ag / al
    return 100 - 100 / t

def ema(c, n):
    k = 2 / (n + 1)
    e = c[0]
    for p in c[1:]:
        e = e + p * k - e * k
    return e

def analyze(s):
    c = klines(s)
    if not c:
        return None
    p = c[-1]
    r = rsi(c)
    e20 = ema(c, 20)
    e50 = ema(c, 50)
    sc = 0
    if r < 50:
        sc += 1
    if p > e20:
        sc += 1
    if e20 > e50:
        sc += 1
    return [p, r, sc]

def send(t):
    if CHAT[0]:
        try:
            bot.send_message(CHAT[0], t)
        except Exception as e:
            print("SEND FAIL", e, flush=True)
    print(t, flush=True)

def loop():
    time.sleep(10)
    send("Машинка запущена ✅")
    while True:
        try:
            for s in SYMS:
                d = analyze(s)
                if not d:
                    continue
                p = d[0]
                if s in POS:
                    en = POS[s]
                    pnl = (p - en) / en * 100
                    if pnl >= 4:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(f"✅ ПРОДАЖА {s}\nПрибыль: {round(pnl, 2)}%\nБаланс: {round(BAL[0], 2)} $")
                    elif pnl <= -2.5:
                        del POS[s]
                        BAL[0] += 50 * pnl / 100
                        send(f"🛑 СТОП {s}\nУбыток: {round(pnl, 2)}%\nБаланс: {round(BAL[0], 2)} $")
                    continue
                if d[2] >= 2:
                    POS[s] = p
                    send(f"🟢 ПОКУПКА {s}\nЦена: {round(p, 2)}\nСкор: {d[2]}/3\nRSI: {round(d[1], 1)}")
            time.sleep(60)
        except Exception as e:
            print("LOOP FAIL", e, flush=True)
            time.sleep(60)

@bot.message_handler(commands=["start"])
def st(m):
    CHAT[0] = m.chat.id
    bot.reply_to(m, "Привет! Я Машинка 🤖\nКоманды:\n/signal - сигналы\n/status - позиции\n/balance - баланс")

@bot.message_handler(commands=["signal"])
def sg(m):
    t = "📊 Сигналы:\n\n"
    for s in SYMS:
        d = analyze(s)
        if not d:
            t += f"{s} - нет данных\n"
            continue
        t += f"{s} {round(d[0], 2)} | Скор: {d[2]}/3 | RSI: {round(d[1], 1)}\n"
    bot.reply_to(m, t)

@bot.message_handler(commands=["status"])
def sts(m):
    if not POS:
        bot.reply_to(m, "Нет открытых позиций. Ждём сигнал... 👀")
        return
    t = "📈 Позиции:\n"
    for s in POS:
        t += f"{s} - вход: {round(POS[s], 2)}\n"
    t += f"\nБаланс: {round(BAL[0], 2)} $"
    bot.reply_to(m, t)

@bot.message_handler(commands=["balance"])
def bal(m):
    bot.reply_to(m, f"💰 Баланс: {round(BAL[0], 2)} $")

# Flask в отдельном потоке
tf = threading.Thread(target=run_flask, daemon=True)
tf.start()
print("FLASK THREAD OK", flush=True)

# Цикл в отдельном потоке
th1 = threading.Thread(target=loop, daemon=True)
th1.start()
print("LOOP THREAD OK", flush=True)

# Бот в главном потоке - теперь процесс не закроется
print("BOT START", flush=True)
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("BOT FAIL", e, flush=True)
        time.sleep(5)
