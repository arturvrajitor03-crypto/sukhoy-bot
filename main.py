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

SYMBOLS = {
    "ЗОЛОТО": "XAUUSDT",
    "БИТКОИН": "BTCUSDT",
    "ЭФИРИУМ": "ETHUSDT",
    "НЕФТЬ": "CL=F",
}
BINANCE_MAP = {"XAUUSDT": "PAXGUSDT", "BTCUSDT": "BTCUSDT", "ETHUSDT": "ETHUSDT"}
last_signal_time = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, *args):
        pass

def get_history(symbol):
    if symbol == "CL=F":
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=15m&range=5d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, timeout=10, headers=headers).json()
            closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [float(x) for x in closes if x is not None]
            return closes
        except Exception:
            return []
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=15&limit=200"
        r = requests.get(url, timeout=10).json()
        if r.get("result") and r["result"].get("list"):
            closes = [float(x[4]) for x in r["result"]["list"][::-1]]
            if len(closes) > 50:
                return closes
    except Exception:
        pass
    try:
        bsym = BINANCE_MAP.get(symbol, symbol)
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={bsym}&interval=15m&limit=200"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        if len(closes) > 50:
            return closes
    except Exception:
        pass
    try:
        bsym = BINANCE_MAP.get(symbol, symbol)
        url = f"https://api.binance.us/api/v3/klines?symbol={bsym}&interval=15m&limit=200"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        if len(closes) > 50:
            return closes
    except Exception:
        pass
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
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        ag = (ag * (period-1) + gains[i]) / period
        al = (al * (period-1) + losses[i]) / period
    if al == 0:
        return 90
    rs = ag / al
    return 100 - (100 / (1 + rs))

def calc_ema(closes, period):
    if not closes:
        return 0
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for p in closes[period:]:
        ema = p * k + ema * (1 - k)
    return ema

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text("🎯 СИГНАЛЬНЫЙ БОТ ВКЛЮЧЕН!\nЯ сам НЕ торгую, только пишу сигналы.\nТы сам решаешь брать или нет.\n\n/price - цены\n/test - проверить сейчас")

async def price_cmd(update, context):
    txt = "ЦЕНЫ:\n\n"
    for name, sym in SYMBOLS.items():
        closes = get_history(sym)
        if not closes:
            txt += f"{name}: нет данных\n"
            continue
        price = closes[-1]
        rsi = calc_rsi(closes)
        ema9 = calc_ema(closes, 9)
        ema21 = calc_ema(closes, 21)
        ema50 = calc_ema(closes, 50)
        if ema9 > ema21 and ema21 > ema50:
            trend = "ВВЕРХ ⬆️"
        elif ema9 < ema21 and ema21 < ema50:
            trend = "ВНИЗ ⬇️"
        else:
            trend = "БОК ➡️ ЖДЁМ"
        txt += f"{name}: {price:.2f} | RSI {rsi:.1f} | {trend}\n"
    await update.message.reply_text(txt)

async def test_cmd(update, context):
    await check_logic(context.bot, force=True)
    await update.message.reply_text("Проверка сделана! Смотри сигналы выше, если были.")

async def check_logic(bot, force=False):
    for name, sym in SYMBOLS.items():
        try:
            closes = get_history(sym)
            if len(closes) < 50:
                continue
            price = closes[-1]
            rsi = calc_rsi(closes)
            ema9 = calc_ema(closes, 9)
            ema21 = calc_ema(closes, 21)
            ema50 = calc_ema(closes, 50)
            print(f"{name} Цена {price} RSI {rsi:.1f} EMA9 {ema9:.2f} EMA21 {ema21:.2f} EMA50 {ema50:.2f}", flush=True)

            # Пауза 2 часа между сигналами по одной монете
            if not force and name in last_signal_time and time.time() - last_signal_time[name] < 7200:
                continue

            # ТОЛЬКО СИЛЬНЫЙ СИГНАЛ
            is_up = ema9 > ema21 and ema21 > ema50 and rsi > 40 and rsi < 60 and price > ema21
            is_down = ema9 < ema21 and ema21 < ema50 and rsi > 40 and rsi < 60 and price < ema21

            if is_up:
                last_signal_time[name] = time.time()
                tp = price * 1.015
                sl = price * 0.995
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 СИГНАЛ ВВЕРХ - {name} BUY\nЦена {price:.2f} RSI {rsi:.1f}\nEMA9 {ema9:.2f} EMA21 {ema21:.2f} EMA50 {ema50:.2f}\nЕсли берёшь: ТП {tp:.2f} СЛ {sl:.2f}\nЯ сам НЕ открыл, решаешь ты!")
                continue
            if is_down:
                last_signal_time[name] = time.time()
                tp = price * 0.985
                sl = price * 1.005
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 СИГНАЛ ВНИЗ - {name} SELL\nЦена {price:.2f} RSI {rsi:.1f}\nEMA9 {ema9:.2f} EMA21 {ema21:.2f} EMA50 {ema50:.2f}\nЕсли берёшь: ТП {tp:.2f} СЛ {sl:.2f}\nЯ сам НЕ открыл, решаешь ты!")
                continue
        except Exception as e:
            print(f"Ошибка {name}: {e}", flush=True)

async def check_job(context):
    await check_logic(context.bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем СИГНАЛЬНОГО БОТА...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("test", test_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_job, interval=300, first=5)
            print("СИГНАЛЬНЫЙ БОТ запущен!", flush=True)
            app.run_polling(drop_pending_updates=True, stop_signals=None)
        except Exception as e:
            print(f"Бот упал: {e}", flush=True)
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
