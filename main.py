import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")

BALANCE = 1000.0
TRADE_SIZE = 0.1  # 10% от баланса на сделку
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
    return 4044.0

def get_rsi(prices, period=14):
    if len(prices)<period+1: return 50
    gains=losses=0
    for i in range(1,period+1):
        diff=prices[-i]-prices[-i-1]
        if diff>0: gains+=diff
        else: losses+= -diff
    if losses==0: return 90
    rs=gains/losses
    return 100 - (100/(1+rs))

def get_signal(price):
    price_history.append(price)
    rsi=get_rsi(list(price_history))
    if rsi>72: return "SELL", min(95, int(rsi+15)), rsi
    if rsi<28: return "BUY", min(95, int(100-rsi)), rsi
    if 45<rsi<55: return "БОКОВИК", 73, rsi
    return "БОКОВИК", 60, rsi

@app.route('/')
def home():
    return f"V17.13 TRADING Gold {get_gold_price()} TOKEN OK",200
@app.route('/health')
def health(): return "OK",200

def run_telegram():
    if not BOT_TOKEN:
        print("NO TOKEN"); time.sleep(60); return
    import telebot
    bot=telebot.TeleBot(BOT_TOKEN)
    print("V17.13 TRADING polling started!")

    @bot.message_handler(commands=['start'])
    def s(m): bot.reply_to(m,"V17.13 TRADING LIVE\n/check - цена\n/trades - сделки\n/status - баланс\nАвтотрейдинг каждые 2 мин")

    @bot.message_handler(commands=['check'])
    def chk(m):
        p=get_gold_price(); sig,perc,rsi=get_signal(p)
        bot.reply_to(m,f"V17.13 TRADING Gold {p}\n{sig} {perc}% RSI {rsi:.1f}\nЦена {p}\nВремя {datetime.now().strftime('%H:%M %d.%m')}\nИсточник Gold-API/Bybit\nБаланс {BALANCE:.2f}$\nСделок открыто: {len(open_trades)}")

    @bot.message_handler(commands=['trades'])
    def tr(m):
        if not open_trades: bot.reply_to(m,f"Нет открытых сделок\nБаланс {BALANCE:.2f}$\nGold {get_gold_price()}")
        else: bot.reply_to(m,"\n".join(open_trades[-5:]))

    @bot.message_handler(commands=['status'])
    def st(m): bot.reply_to(m,f"V17.13 TRADING\nGold: {get_gold_price()}\nБаланс: {BALANCE}$\nИстория цен: {len(price_history)}\nВозможности: ищу RSI>72 или <28")

    def auto_trader():
        global BALANCE
        while True:
            time.sleep(120) # каждые 2 мин проверяет возможность
            try:
                p=get_gold_price(); sig,perc,rsi=get_signal(p)
                # НОРМАЛЬНАЯ ВОЗМОЖНОСТЬ = RSI сильный
                if perc>=90 and (sig=="SELL" or sig=="BUY"):
                    trade_msg=f"🔥 ВОЗМОЖНОСТЬ {sig} {perc}% RSI {rsi:.1f} Цена {p} Время {datetime.now().strftime('%H:%M')}"
                    open_trades.append(trade_msg)
                    print(trade_msg)
                    try:
                        # если указан CHAT_ID - шлет автоматом
                        if CHAT_ID: bot.send_message(CHAT_ID, trade_msg)
                        else: bot.send_message(BOT_TOKEN.split(':')[0], trade_msg) # fallback
                    except: pass
                    # шлем всем кто писал боту недавно - через last chat
                    try:
                        bot.send_message(m.chat.id, trade_msg) 
                    except: pass
            except Exception as e: print(f"trader err {e}")

    threading.Thread(target=auto_trader, daemon=True).start()
    bot.infinity_polling(none_stop=True, timeout=60)

if __name__=='__main__':
    threading.Thread(target=run_telegram, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
