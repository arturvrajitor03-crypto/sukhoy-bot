import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")
price_history = deque(maxlen=100)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4042))
    except:
        return 4042.8

@app.route('/')
def home():
    return "V22 BEAUTY RU Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V22 BEAUTY RU started")

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = "GOLD BOT V22\n\n/check - proverka\n/status - balans"
        bot.reply_to(m, txt)

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        if len(price_history) > 14:
            gains = 0
            losses = 0
            lst = list(price_history)
            for i in range(1, 15):
                d = lst[-i] - lst[-i-1]
                if d > 0:
                    gains += d
                else:
                    losses += -d
            if losses == 0:
                rsi = 80
            else:
                rs = gains / losses
                rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50

        if rsi < 32:
            sig = "BUY"
            perc = 90
            emo = "🟢"
            action = "POKUPAT"
            tp = p + 30
            sl = p - 20
        elif rsi > 68:
            sig = "SELL"
            perc = 90
            emo = "🔴"
            action = "PRODAVAT"
            tp = p - 30
            sl = p + 20
        else:
            sig = "BOKOVIK"
            perc = 60
            emo = "⚪️"
            action = "JDAT"
            tp = p
            sl = p

        ema_val = sum(list(price_history)[-20:])/20 if len(price_history)>=20 else p

        a1 = "🔰 GOLD PRO V22\n\n"
        a2 = "{} SIGNAL: {} {}\n".format(emo, sig, perc)
        a3 = "💬 Deistvie: {}\n\n".format(action)
        a4 = "💰 Tsena:\n{:.2f} $\n\n".format(p)
        a5 = "📊 Indikatory:\n"
        a6 = "├ RSI: {:.1f}\n".format(rsi)
        a7 = "├ EMA20: {:.2f} $\n".format(ema_val)
        a8 = "└ Uverennost: {}%\n\n".format(perc)
        a9 = "🎯 Plan:\n"
        a10 = "├ Vkhod: {:.2f} $\n".format(p)
        a11 = "├ TP: {:.2f} $ (+30)\n".format(tp)
        a12 = "└ SL: {:.2f} $ (-20)\n\n".format(sl)
        a13 = "⏰ Vremya: {}\n".format(datetime.now().strftime("%H:%M %d.%m"))
        a14 = "💼 Balans: 1000.00 $\n"
        a15 = "🔗 Gold-API / Bybit"

        msg = a1+a2+a3+a4+a5+a6+a7+a8+a9+a10+a11+a12+a13+a14+a15
        bot.reply_to(m, msg)

    @bot.message_handler(commands=['status'])
    def status(m):
        msg = "STATUS V22\nPrice: {:.2f}\nHistory: {}".format(get_price(), len(price_history))
        bot.reply_to(m, msg)

    bot.infinity_polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
