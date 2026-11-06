import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=200)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4045))
    except:
        return 4045.0

@app.route('/')
def home():
    return "V27 ULTIMATE SIMPLE Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V27 STARTED")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "V27 BEST READY /check /status")

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        lst = list(price_history)
        if len(lst) < 30:
            base = p - 15
            lst = [base + i*0.6 for i in range(40)]
            lst.append(p)

        gains = 0
        losses = 0
        for i in range(1, 15):
            d = lst[-i] - lst[-i-1]
            if d > 0:
                gains += d
            else:
                losses += -d
        if losses < 0.1:
            rsi = 74.0
        else:
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs))

        ema20 = sum(lst[-20:]) / 20
        ema50 = sum(lst[-50:]) / 50 if len(lst) >= 50 else ema20

        if rsi < 30:
            sig = "POKUPKA"
            perc = 92
            emo = "🟢"
            tp = p + 35
            sl = p - 18
            desc = "Pereprodan - ROST"
        elif rsi < 45:
            sig = "POKUPKA"
            perc = 82
            emo = "🟢"
            tp = p + 30
            sl = p - 18
            desc = "Slabost prodavcov"
        elif rsi > 70:
            sig = "PRODAZHA"
            perc = 92
            emo = "🔴"
            tp = p - 35
            sl = p + 18
            desc = "Perekuplen - PADENIE"
        elif rsi > 55:
            sig = "PRODAZHA"
            perc = 82
            emo = "🔴"
            tp = p - 30
            sl = p + 18
            desc = "Slabost pokupateley"
        else:
            sig = "BOKOVIK"
            perc = 55
            emo = "⚪️"
            tp = p + 20
            sl = p - 20
            desc = "Nyet trenda - JDEM"

        l1 = "====================\n"
        l2 = "GOLD PRO V27 BEST\n"
        l3 = "====================\n\n"
        l4 = "{} {} {}%\n".format(emo, sig, perc)
        l5 = "{}\n\n".format(desc)
        l6 = "GOLD: {:.2f} $\n\n".format(p)
        l7 = "INDIKATORY:\n"
        l8 = "RSI: {:.1f}\n".format(rsi)
        l9 = "EMA20: {:.2f}\n".format(ema20)
        l10 = "EMA50: {:.2f}\n".format(ema50)
        l11 = "UVERENNOST: {}%\n\n".format(perc)
        l12 = "PLAN:\n"
        l13 = "Vkhod: {:.2f}\n".format(p)
        l14 = "Take: {:.2f}\n".format(tp)
        l15 = "Stop: {:.2f}\n\n".format(sl)
        l16 = "Time: {}\n".format(datetime.now().strftime("%H:%M %d.%m"))
        l17 = "===================="

        msg = l1+l2+l3+l4+l5+l6+l7+l8+l9+l10+l11+l12+l13+l14+l15+l16+l17
        bot.reply_to(m, msg)

    @bot.message_handler(commands=['status'])
    def status(m):
        bot.reply_to(m, "V27 OK {:.2f}".format(get_price()))

    bot.infinity_polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
