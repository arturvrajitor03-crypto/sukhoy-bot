import os
import logging
import requests
import threading
import time
import traceback
import asyncio
import statistics
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
MAX_PER_SYMBOL = 1

SYMBOLS = {
    "ЗОЛОТО": "XAUUSDT",
    "БИТКОИН": "BTCUSDT",
    "ЭФИРИУМ": "ETHUSDT",
    "НЕФТЬ": "CL=F",
}
BINANCE_MAP = {"XAUUSDT": "PAXGUSDT", "BTCUSDT": "BTCUSDT", "ETHUSDT": "ETHUSDT"}
positions = {}
last_close_time = {}

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

def get_tp_sl(pos):
    entry = pos["price"]
    if pos["type"] == "BUY":
        return entry * 1.01, entry * 0.995
    else:
        return entry * 0.99, entry * 1.005

def count_for(name):
    c = 0
    for k in positions.keys():
        if k.startswith(name):
            c += 1
    return c

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"🎯 СЧЁТ\n\nСтарт: {START_BALANCE:.2f}$\nСейчас: {BALANCE:.2f}$\nПрибыль: {znak}{profit:.2f}$\n"
    if positions:
        txt += "\n--- ОТКРЫТЫЕ ---\n"
        for name, pos in positions.items():
            tp, sl = get_tp_sl(pos)
            txt += f"\n{name}: {pos['type']} по {pos['price']:.2f} ТП {tp:.2f} СЛ {sl:.2f}"
    else:
        txt += "\nНет сделок"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text(f"🎯 БОТ ВКЛЮЧЕН!\nВВЕРХ = BUY, ВНИЗ = SELL\n/close - закрыть все\n\n{balance_text()}\n\n/balance - деньги\n/status - позиции\n/price - цены\n/close - закрыть всё")

async def balance_cmd(update, context):
    await update.message.reply_text(balance_text())

async def status_cmd(update, context):
    await update.message.reply_text(balance_text())

async def close_cmd(update, context):
    global BALANCE
    if not positions:
        await update.message.reply_text("Нет открытых сделок")
        return
    txt = "ЗАКРЫВАЮ ВСЕ:\n"
    for key in list(positions.keys()):
        pos = positions[key]
        closes = get_history(SYMBOLS.get(key.split(" #")[0], "XAUUSDT"))
        price = closes[-1] if closes else pos["price"]
        if pos["type"] == "BUY":
            pnl_pct = (price - pos["price"]) / pos["price"] * 100
        else:
            pnl_pct = (pos["price"] - price) / pos["price"] * 100
        pnl = pos["amount"] * pnl_pct / 100
        BALANCE += pnl
        txt += f"\n{key} {pos['type']} Вход {pos['price']:.2f} Выход {price:.2f} ПнЛ {pnl:+.2f}$"
        del positions[key]
    txt += f"\n\n{balance_text()}"
    await update.message.reply_text(txt)

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
        trend = "ВВЕРХ ⬆️ BUY" if ema9 > ema21 else "ВНИЗ ⬇️ SELL"
        txt += f"{name}: {price:.2f} | RSI {rsi:.1f} | EMA9 {ema9:.2f} EMA21 {ema21:.2f} | {trend} | Сделок: {count_for(name)}/1\n"
    txt += f"\n{balance_text()}"
    await update.message.reply_text(txt)

async def test_cmd(update, context):
    await check_gold_logic(context.bot)
    await update.message.reply_text(f"🎯 ПРОВЕРКА ЗАПУЩЕНА!\n\n{balance_text()}")

async def check_gold_logic(bot):
    global BALANCE
    for name, sym in SYMBOLS.items():
        try:
            closes = get_history(sym)
            if len(closes) < 50:
                continue
            price = closes[-1]
            rsi = calc_rsi(closes)
            ema9 = calc_ema(closes, 9)
            ema21 = calc_ema(closes, 21)
            # Последние 3 свечи - куда реально идёт цена
            last3_up = closes[-1] > closes[-2] > closes[-3]
            last3_down = closes[-1] < closes[-2] < closes[-3]
            # НОРМАЛЬНАЯ ЛОГИКА - 3 подтверждения сразу
            # ВВЕРХ = EMA9 выше EMA21 + цена растёт + RSI > 50
            is_up = ema9 > ema21 and rsi > 50 and rsi < 72 and (last3_up or price > ema9)
            # ВНИЗ = EMA9 ниже EMA21 + цена падает + RSI < 50
            is_down = ema9 < ema21 and rsi < 50 and rsi > 28 and (last3_down or price < ema9)
            print(f"{name} Цена {price} RSI {rsi:.1f} EMA9 {ema9:.2f} EMA21 {ema21:.2f} ВВЕРХ={is_up} ВНИЗ={is_down}", flush=True)
            keys = [k for k in list(positions.keys()) if k.startswith(name)]
            for key in keys:
                pos = positions.get(key)
                if not pos:
                    continue
                entry = pos["price"]
                amount = pos["amount"]
                if pos["type"] == "BUY":
                    pnl_pct = (price - entry) / entry * 100
                else:
                    pnl_pct = (entry - price) / entry * 100
                if pnl_pct >= 1.0:
                    profit = amount * pnl_pct / 100
                    BALANCE += profit
                    last_close_time[name] = time.time()
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"ПЛЮС! {key} {pos['type']}\nВход {entry:.2f} Выход {price:.2f}\nПрибыль +{profit:.2f}$\n\n{balance_text()}")
                    del positions[key]
                    continue
                if pnl_pct <= -0.5:
                    loss = amount * pnl_pct / 100
                    BALANCE += loss
                    last_close_time[name] = time.time()
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"СТОП {key} {pos['type']}\nВход {entry:.2f} Выход {price:.2f}\nУбыток {loss:.2f}$\n\n{balance_text()}")
                    del positions[key]
                    continue
                # ПЕРЕВОРОТ - тренд поменялся
                if pos["type"] == "SELL" and is_up:
                    loss = amount * pnl_pct / 100
                    BALANCE += loss
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"🔄 ПЕРЕВОРОТ! {key} SELL закрыт, тренд стал ВВЕРХ\nВход {entry:.2f} Выход {price:.2f} ПнЛ {loss:+.2f}$")
                    del positions[key]
                    continue
                if pos["type"] == "BUY" and is_down:
                    loss = amount * pnl_pct / 100
                    BALANCE += loss
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"🔄 ПЕРЕВОРОТ! {key} BUY закрыт, тренд стал ВНИЗ\nВход {entry:.2f} Выход {price:.2f} ПнЛ {loss:+.2f}$")
                    del positions[key]
                    continue
            if count_for(name) >= MAX_PER_SYMBOL:
                continue
            if name in last_close_time and time.time() - last_close_time[name] < 300:
                continue
            amount = LOT * price
            if name in ["БИТКОИН", "ЭФИРИУМ"]:
                amount = 500.0
            if is_up:
                n = count_for(name) + 1
                key = f"{name} #{n}"
                positions[key] = {"type": "BUY", "price": price, "amount": amount, "lot": LOT}
                tp, sl = get_tp_sl(positions[key])
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 ВВЕРХ - ПОКУПКА! {key}\nRSI {rsi:.1f} Цена {price:.2f} EMA9 {ema9:.2f} EMA21 {ema21:.2f}\nТП {tp:.2f} СЛ {sl:.2f}\n\n{balance_text()}")
                continue
            if is_down:
                n = count_for(name) + 1
                key = f"{name} #{n}"
                positions[key] = {"type": "SELL", "price": price, "amount": amount, "lot": LOT}
                tp, sl = get_tp_sl(positions[key])
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 ВНИЗ - ПРОДАЖА! {key}\nRSI {rsi:.1f} Цена {price:.2f} EMA9 {ema9:.2f} EMA21 {ema21:.2f}\nТП {tp:.2f} СЛ {sl:.2f}\n\n{balance_text()}")
                continue
        except Exception as e:
            print(f"Ошибка {name}: {e}", flush=True)

async def check_gold_job(context):
    await check_gold_logic(context.bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем БОТА...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("balance", balance_cmd))
            app.add_handler(CommandHandler("test", test_cmd))
            app.add_handler(CommandHandler("close", close_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_gold_job, interval=60, first=5)
            print("БОТ запущен!", flush=True)
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
