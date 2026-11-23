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
MAX_PER_SYMBOL = 2

SYMBOLS = {
    "ЗОЛОТО": "PAXGUSDT",
    "БИТКОИН": "BTCUSDT",
    "ЭФИРИУМ": "ETHUSDT",
    "НЕФТЬ": "CL=F",
}
positions = {}

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
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=15m&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, timeout=10, headers=headers).json()
            closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [float(x) for x in closes if x is not None]
            return closes
        except Exception:
            return []
    urls = [
        f"https://api.binance.us/api/v3/klines?symbol={symbol}&interval=15m&limit=100",
        f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=15m&limit=100",
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

def calc_ema(closes, period):
    if not closes:
        return 0
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = closes[0]
    for p in closes[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0
    ema12 = calc_ema(closes, 12)
    ema26 = calc_ema(closes, 26)
    macd = ema12 - ema26
    prev_ema12 = calc_ema(closes[:-1], 12)
    prev_ema26 = calc_ema(closes[:-1], 26)
    prev_macd = prev_ema12 - prev_ema26
    signal = (macd + prev_macd) / 2
    return macd, signal

def get_tp_sl(pos):
    entry = pos["price"]
    if pos["type"] == "BUY":
        return entry * 1.02, entry * 0.985
    else:
        return entry * 0.98, entry * 1.015

def count_for(name):
    c = 0
    for k in positions.keys():
        if k.startswith(name):
            c += 1
    return c

def balance_text():
    profit = BALANCE - START_BALANCE
    znak = "+" if profit >= 0 else ""
    txt = f"СЧЁТ АГРЕССИВНЫЙ - 8 СДЕЛОК MAX\n\nСтарт: {START_BALANCE:.2f}$\nСейчас: {BALANCE:.2f}$\nПрибыль: {znak}{profit:.2f}$\nЛот: {LOT}\n"
    if positions:
        txt += "\n--- ОТКРЫТЫЕ СДЕЛКИ ---\n"
        for name, pos in positions.items():
            tp, sl = get_tp_sl(pos)
            txt += f"\n{name}: {pos['type']} по {pos['price']:.2f} ТП {tp:.2f} СЛ {sl:.2f}"
    else:
        txt += "\nОткрытых сделок нет - бот ищет вход"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    msg = f"БОТ-АГРЕССИВНЫЙ АКТИВЕН!\n\nПо 2 сделки на каждый рынок!\nВсего максимум 8 сделок!\n1. ЗОЛОТО x2\n2. БИТКОИН x2\n3. ЭФИРИУМ x2\n4. НЕФТЬ x2\n\nПроверка каждые 5 минут!\n\n/balance - деньги\n/status - позиции\n/price - цены\n/test - открыть 2 тестовые сделки!"
    await update.message.reply_text(msg)

async def balance_cmd(update, context):
    await update.message.reply_text(balance_text())

async def status_cmd(update, context):
    await update.message.reply_text(balance_text())

async def price_cmd(update, context):
    txt = "ЦЕНЫ ВСЕХ 4 РЫНКОВ:\n\n"
    for name, sym in SYMBOLS.items():
        closes = get_history(sym)
        if not closes:
            txt += f"{name}: нет данных\n"
            continue
        price = closes[-1]
        rsi = calc_rsi(closes)
        ema200 = calc_ema(closes, 100)
        trend = "ВВЕРХ" if price > ema200 else "ВНИЗ"
        txt += f"{name}: {price:.2f} | RSI {rsi:.1f} | Тренд {trend} | Сделок: {count_for(name)}/2\n"
    txt += f"\n{balance_text()}"
    await update.message.reply_text(txt)

async def test_cmd(update, context):
    closes = get_history("PAXGUSDT")
    if not closes:
        await update.message.reply_text("Нет данных по золоту")
        return
    price = closes[-1]
    opened = 0
    for i in range(2):
        key = f"ЗОЛОТО #{i+1}"
        if key not in positions:
            positions[key] = {"type": "BUY", "price": price, "amount": LOT * price, "lot": LOT}
            opened += 1
    if opened == 0:
        await update.message.reply_text("Уже 2 сделки по золоту! Смотри /status")
        return
    await update.message.reply_text(f"ОТКРЫЛА {opened} ТЕСТОВЫЕ СДЕЛКИ ПО ЗОЛОТУ!\nЦена: {price:.2f}\n\n{balance_text()}")

async def check_gold_logic(bot):
    global BALANCE
    for name, sym in SYMBOLS.items():
        try:
            closes = get_history(sym)
            if len(closes) < 50:
                continue
            price = closes[-1]
            rsi = calc_rsi(closes)
            ema50 = calc_ema(closes, 50)
            ema200 = calc_ema(closes, 100)
            macd, signal = calc_macd(closes)
            last_change = (closes[-1] - closes[-4]) / closes[-4] * 100
            if abs(last_change) > 1.5:
                continue
            print(f"{name} Цена {price} RSI {rsi:.1f} Сделок {count_for(name)}", flush=True)
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
                if pnl_pct >= 2.0:
                    profit = amount * pnl_pct / 100
                    BALANCE += profit
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"ЗАКРЫЛ В ПЛЮС! {key} {pos['type']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nПрибыль: +{profit:.2f}$\n\n{balance_text()}")
                    del positions[key]
                    continue
                if pnl_pct <= -1.5:
                    loss = amount * pnl_pct / 100
                    BALANCE += loss
                    if CHAT_ID != 0:
                        await bot.send_message(chat_id=CHAT_ID, text=f"ЗАКРЫЛ ПО СТОПУ {key} {pos['type']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nУбыток: {loss:.2f}$\n\n{balance_text()}")
                    del positions[key]
                    continue
            if count_for(name) >= MAX_PER_SYMBOL:
                continue
            amount = LOT * price
            if name in ["БИТКОИН", "ЭФИРИУМ"]:
                amount = 500.0
            if price > ema200 and rsi < 45 and macd > signal:
                n = count_for(name) + 1
                key = f"{name} #{n}"
                positions[key] = {"type": "BUY", "price": price, "amount": amount, "lot": LOT}
                tp, sl = get_tp_sl(positions[key])
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"СИГНАЛ ПОКУПКА! {key}\nRSI: {rsi:.1f}\nЦена: {price:.2f}\nТП: {tp:.2f} СЛ: {sl:.2f}\n\n{balance_text()}")
                continue
            if price < ema200 and rsi > 55 and macd < signal:
                n = count_for(name) + 1
                key = f"{name} #{n}"
                positions[key] = {"type": "SELL", "price": price, "amount": amount, "lot": LOT}
                tp, sl = get_tp_sl(positions[key])
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"СИГНАЛ ПРОДАЖА! {key}\nRSI: {rsi:.1f}\nЦена: {price:.2f}\nТП: {tp:.2f} СЛ: {sl:.2f}\n\n{balance_text()}")
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
            print("Запускаем Бота...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("balance", balance_cmd))
            app.add_handler(CommandHandler("test", test_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_gold_job, interval=300, first=10)
            print("Бот запущен!", flush=True)
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
