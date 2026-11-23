import os
import logging
import requests
import threading
import time
import traceback
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0") or "0")
PORT = int(os.getenv("PORT", "10000"))

BALANCE = 500.0
START_BALANCE = 500.0
TRADE_AMOUNT = 50.0
position = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, *args):
        pass

def get_history():
    urls = [
        "https://api.binance.us/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
        "https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            closes = [float(x[4]) for x in r]
            if len(closes) > 50:
                return closes
        except Exception:
            continue
    return []

def calc_rsi(closes, period=14):
    if len(closes) < period+1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i]-closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:])/period
    al = sum(losses[-period:])/period
    if al == 0:
        return 100
    rs = ag/al
    return 100 - (100/(1+rs))

def calc_ema(closes, period, current_price=None):
    if not closes:
        return current_price if current_price else 0
    if len(closes) < period:
        return closes[-1]
    k = 2/(period+1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p*k + ema*(1-k)
    return ema

def get_gold_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=10, headers=headers)
        item = r.json()["items"][0]
        return float(item["curr"]), float(item["chg"])
    except Exception:
        pass
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10, headers=headers)
        d = r.json()
        return float(d["price"]), float(d.get("change24h", 0))
    except Exception:
        pass
    raise Exception("API ne otvechayut")

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"VIRTUALNIY SCHET\n\nStart: {START_BALANCE:.2f}$\nSeychas: {BALANCE:.2f}$\nPribil: {znak}{profit:.2f}$\n"
    if position:
        txt += f"\nOtkrita: {position['type']} {position['amount']}$ po {position['price']:.2f}"
    else:
        txt += "\nOtkritih sdelok net"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text(f"Bot PRO AKTIVNIY rabotaet!\n\nBUY + SELL - v obe storoni!\nVirtual: 500$\n\n/balance - deneg\n/status - pozicii\n/price - cena")

async def balance_cmd(update, context):
    await update.message.reply_text(balance_text())

async def status_cmd(update, context):
    await update.message.reply_text(balance_text())

async def price_cmd(update, context):
    try:
        price, chg = get_gold_price()
        closes = get_history()
        rsi = calc_rsi(closes)
        ema = calc_ema(closes, 50, price)
        txt = f"ZOLOTO: {price:.2f}\nIzm: {chg:+.2f}\n\nRSI: {rsi:.1f}\nEMA50: {ema:.2f}\nTrend: {'VVERH' if price > ema else 'VNIZ'}\n\n{balance_text()}"
        await update.message.reply_text(txt)
    except Exception as e:
        await update.message.reply_text(f"Oshibka: {e}")

async def check_gold_logic(bot):
    global BALANCE, position
    try:
        price, chg = get_gold_price()
        closes = get_history()
        rsi = calc_rsi(closes)
        ema = calc_ema(closes, 50, price)
        print(f"Check Price {price} RSI {rsi:.1f} EMA {ema:.2f} Bal {BALANCE} Pos {position}", flush=True)

        # --- ESLI EST OTKRYTA SDELKA - PROVERYAEM ZAKRYTIE ---
        if position:
            entry = position['price']
            if position['type'] == 'BUY':
                pnl_pct = (price - entry) / entry * 100
            else:  # SELL
                pnl_pct = (entry - price) / entry * 100

            if pnl_pct >= 2.0:
                profit = TRADE_AMOUNT * pnl_pct / 100
                BALANCE += profit
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"✅ ZAKRYLI V PLYUS! {position['type']}\nVhod: {entry:.2f}\nVihod: {price:.2f}\nPribil: +{profit:.2f}$\n\n{balance_text()}")
                position = None
                return
            if pnl_pct <= -1.5:
                loss = TRADE_AMOUNT * pnl_pct / 100
                BALANCE += loss
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"🛑 STOP-LOSS {position['type']}\nVhod: {entry:.2f}\nVihod: {price:.2f}\nUbitok: {loss:.2f}$\n\n{balance_text()}")
                position = None
                return
            return

        # --- NET SDELKI - ISHEM NOVUYU, V OBE STORONI ---
        # 1. BUY - deshevo + trend vverh
        if rsi < 40 and price > ema:
            position = {'type': 'BUY', 'price': price, 'amount': TRADE_AMOUNT}
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"🟢 SIGNAL BUY!\nCena: {price:.2f}\nRSI: {rsi:.1f} - deshevo!\nEMA50: {ema:.2f} - trend vverh\nSumma: {TRADE_AMOUNT}$\n\n{balance_text()}")
            return

        # 2. SELL - dorogo + trend vniz
        if rsi > 60 and price < ema:
            position = {'type': 'SELL', 'price': price, 'amount': TRADE_AMOUNT}
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"🔴 SIGNAL SELL!\nCena: {price:.2f}\nRSI: {rsi:.1f} - dorogo!\nEMA50: {ema:.2f} - trend vniz\nSumma: {TRADE_AMOUNT}$\n\n{balance_text()}")
            return

        # 3. SELL esli ochen perekuplen, dazhe bez trenda - chtob bil aktivnim
        if rsi > 75:
            position = {'type': 'SELL', 'price': price, 'amount': TRADE_AMOUNT}
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"🔴 SIGNAL SELL! PEREKUPLEN!\nCena: {price:.2f}\nRSI: {rsi:.1f} - ochen dorogo!\nSumma: {TRADE_AMOUNT}$\n\n{balance_text()}")
            return

    except Exception as e:
        print(f"Check oshibka: {e}", flush=True)

async def check_gold_job(context):
    await check_gold_logic(context.bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            print("Zapuskaem Telegram bot...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("balance", balance_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_gold_job, interval=900, first=10)
            print("Bot PRO zapushchen!", flush=True)
            app.run_polling(drop_pending_updates=True, stop_signals=None)
        except Exception as e:
            print(f"Bot upal, perezapusk: {e}", flush=True)
            traceback.print_exc()
            time.sleep(10)

def main():
    if TOKEN:
        t = threading.Thread(target=run_bot, daemon=True)
        t.start()
        print("Bot thread zapushchen", flush=True)
    else:
        print("OSHIBKA: Net TELEGRAM_TOKEN!", flush=True)
    print(f"Web server na portu {PORT}...", flush=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("Web server OK!", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
