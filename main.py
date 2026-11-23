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
LOT = 1.00
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

def calc_ema(closes, period, current_price=None):
    if not closes:
        return current_price if current_price else 0
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p * k + ema * (1 - k)
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
        ch = d.get("change24h", 0)
        return float(d["price"]), float(ch)
    except Exception:
        pass
    raise Exception("API не отвечают")

def get_tp_sl(pos):
    entry = pos["price"]
    if pos["type"] == "BUY":
        tp = entry * 1.02
        sl = entry * 0.985
    else:
        tp = entry * 0.98
        sl = entry * 1.015
    return tp, sl

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"ВИРТУАЛЬНЫЙ СЧЁТ\n\nСтарт: {START_BALANCE:.2f}$\nСейчас: {BALANCE:.2f}$\nПрибыль: {znak}{profit:.2f}$\nЛот: {LOT}\n"
    if position:
        tp, sl = get_tp_sl(position)
        txt += f"\nОткрыта: {position['type']} Лот {position['lot']} по {position['price']:.2f}\nСумма: {position['amount']:.2f}$\nТП: {tp:.2f}\nСЛ: {sl:.2f}"
    else:
        txt += "\nОткрытых сделок нет"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    msg = f"Бот ПРО АКТИВЕН работает!\n\nПОКУПКА + ПРОДАЖА\nЛот: {LOT}\nВиртуально: 500$\n\n/balance - деньги\n/status - позиции + ТП/СЛ\n/price - цена"
    await update.message.reply_text(msg)

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
        trend = "ВВЕРХ" if price > ema else "ВНИЗ"
        txt = f"ЗОЛОТО: {price:.2f}\nИзменение: {chg:+.2f}\n\nRSI: {rsi:.1f}\nEMA50: {ema:.2f}\nТренд: {trend}\n\n{balance_text()}"
        await update.message.reply_text(txt)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def check_gold_logic(bot):
    global BALANCE, position
    try:
        price, chg = get_gold_price()
        closes = get_history()
        rsi = calc_rsi(closes)
        ema = calc_ema(closes, 50, price)
        print(f"Проверка Цена {price} RSI {rsi:.1f} EMA {ema:.2f} Баланс {BALANCE} Позиция {position}", flush=True)
        if position:
            entry = position["price"]
            amount = position["amount"]
            if position["type"] == "BUY":
                pnl_pct = (price - entry) / entry * 100
            else:
                pnl_pct = (entry - price) / entry * 100
            tp, sl = get_tp_sl(position)
            if pnl_pct >= 2.0:
                profit = amount * pnl_pct / 100
                BALANCE += profit
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"ЗАКРЫЛИ В ПЛЮС! {position['type']} Лот {position['lot']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nТП был: {tp:.2f}\nПрибыль: +{profit:.2f}$\n\n{balance_text()}")
                position = None
                return
            is_stop = pnl_pct <= -1.5
            if is_stop:
                loss = amount * pnl_pct / 100
                BALANCE += loss
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"СТОП-ЛОСС {position['type']} Лот {position['lot']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nСЛ был: {sl:.2f}\nУбыток: {loss:.2f}$\n\n{balance_text()}")
                position = None
                return
            return
        amount = LOT * price
        if rsi < 40 and price > ema:
            position = {"type": "BUY", "price": price, "amount": amount, "lot": LOT}
            tp, sl = get_tp_sl(position)
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"СИГНАЛ ПОКУПКА!\nЦена: {price:.2f}\nRSI: {rsi:.1f}\nEMA50: {ema:.2f}\nЛот: {LOT}\nСумма: {amount:.2f}$\nТП: {tp:.2f}\nСЛ: {sl:.2f}\n\n{balance_text()}")
            return
        if rsi > 60 and price < ema:
            position = {"type": "SELL", "price": price, "amount": amount, "lot": LOT}
            tp, sl = get_tp_sl(position)
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"СИГНАЛ ПРОДАЖА!\nЦена: {price:.2f}\nRSI: {rsi:.1f}\nEMA50: {ema:.2f}\nЛот: {LOT}\nСумма: {amount:.2f}$\nТП: {tp:.2f}\nСЛ: {sl:.2f}\n\n{balance_text()}")
            return
        if rsi > 75:
            position = {"type": "SELL", "price": price, "amount": amount, "lot": LOT}
            tp, sl = get_tp_sl(position)
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"СИГНАЛ ПРОДАЖА! ПЕРЕКУПЛЕН!\nЦена: {price:.2f}\nRSI: {rsi:.1f}\nЛот: {LOT}\nСумма: {amount:.2f}$\nТП: {tp:.2f}\nСЛ: {sl:.2f}\n\n{balance_text()}")
            return
    except Exception as e:
        print(f"Ошибка проверки: {e}", flush=True)

async def check_gold_job(context):
    await check_gold_logic(context.bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем Телеграм бот...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("balance", balance_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_gold_job, interval=900, first=10)
            print("Бот ПРО запущен!", flush=True)
            app.run_polling(drop_pending_updates=True, stop_signals=None)
        except Exception as e:
            print(f"Бот упал, перезапуск: {e}", flush=True)
            traceback.print_exc()
            time.sleep(10)

def main():
    if TOKEN:
        t = threading.Thread(target=run_bot, daemon=True)
        t.start()
        print("Поток бота запущен", flush=True)
    else:
        print("ОШИБКА: Нет TELEGRAM_TOKEN!", flush=True)
    print(f"Веб сервер на порту {PORT}...", flush=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("Веб сервер ОК!", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
