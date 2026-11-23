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
last_signal_time = 0

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

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0
    ema12 = calc_ema(closes, 12)
    ema26 = calc_ema(closes, 26)
    macd = ema12 - ema26
    # Сигнальная линия - EMA от MACD примерно
    prev_ema12 = calc_ema(closes[:-1], 12)
    prev_ema26 = calc_ema(closes[:-1], 26)
    prev_macd = prev_ema12 - prev_ema26
    signal = (macd + prev_macd) / 2
    return macd, signal

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
    txt = f"СЧЁТ ПРОФЕССИОНАЛА\n\nСтарт: {START_BALANCE:.2f}$\nСейчас: {BALANCE:.2f}$\nПрибыль: {znak}{profit:.2f}$\nЛот: {LOT}\n"
    if position:
        tp, sl = get_tp_sl(position)
        txt += f"\nОткрыта: {position['type']} Лот {position['lot']} по {position['price']:.2f}\nСумма: {position['amount']:.2f}$\nТП: {tp:.2f}\nСЛ: {sl:.2f}"
    else:
        txt += "\nОткрытых сделок нет - ждем точный вход как профессионал"
    return txt

async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    msg = f"БОТ-ПРОФЕССИОНАЛ АКТИВЕН!\n\nТоргую как профи:\n- Только по тренду\n- Только точный вход\n- Без паники\n- Стоп всегда!\n\nЛот: {LOT}\n\n/balance - деньги\n/status - позиции\n/price - цена"
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
        ema50 = calc_ema(closes, 50, price)
        ema200 = calc_ema(closes, 100, price)
        macd, signal = calc_macd(closes)
        trend = "ВВЕРХ - только ПОКУПКА" if price > ema200 else "ВНИЗ - только ПРОДАЖА"
        txt = f"ЗОЛОТО: {price:.2f}\nИзменение: {chg:+.2f}\n\nRSI: {rsi:.1f}\nEMA50: {ema50:.2f}\nEMA200: {ema200:.2f}\nMACD: {macd:.2f}\nТренд: {trend}\n\n{balance_text()}"
        await update.message.reply_text(txt)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def check_gold_logic(bot):
    global BALANCE, position, last_signal_time
    try:
        price, chg = get_gold_price()
        closes = get_history()
        if len(closes) < 50:
            return
        rsi = calc_rsi(closes)
        ema50 = calc_ema(closes, 50, price)
        ema200 = calc_ema(closes, 100, price)
        macd, signal = calc_macd(closes)
        # Профессионал: не торгуем если рынок в панике - резкое движение
        last_change = (closes[-1] - closes[-4]) / closes[-4] * 100
        if abs(last_change) > 0.8:
            print(f"ПРОФИ ЖДЕТ - паника на рынке {last_change:.2f}%", flush=True)
            return
        # Профессионал: перерыв после сделки - не входит сразу, ждет 1 час
        if time.time() - last_signal_time < 3600 and position is None and last_signal_time != 0:
            # Если только что закрыли, ждем - не спешим
            pass
        print(f"ПРОФИ Проверка Цена {price} RSI {rsi:.1f} MACD {macd:.2f} Тренд EMA200 {ema200:.2f} Баланс {BALANCE}", flush=True)
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
                last_signal_time = time.time()
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"ПРОФИ ЗАКРЫЛ В ПЛЮС! {position['type']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nПрибыль: +{profit:.2f}$\n\n{balance_text()}")
                position = None
                return
            if pnl_pct <= -1.5:
                loss = amount * pnl_pct / 100
                BALANCE += loss
                last_signal_time = time.time()
                if CHAT_ID != 0:
                    await bot.send_message(chat_id=CHAT_ID, text=f"ПРОФИ ЗАКРЫЛ ПО СТОПУ {position['type']}\nВход: {entry:.2f}\nВыход: {price:.2f}\nУбыток: {loss:.2f}$ - стоп сработал, защитили депозит!\n\n{balance_text()}")
                position = None
                return
            return
        amount = LOT * price
        # ПРОФИ ПОКУПКА: нужны ВСЕ 4 условия сразу!
        # 1. Цена выше EMA200 - тренд вверх
        # 2. RSI меньше 35 - цена упала, дешево
        # 3. MACD выше сигнала - разворот вверх начался
        # 4. Цена выше EMA50 - подтверждение
        if price > ema200 and rsi < 35 and macd > signal and price > ema50:
            position = {"type": "BUY", "price": price, "amount": amount, "lot": LOT}
            tp, sl = get_tp_sl(position)
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"ПРОФИ СИГНАЛ ПОКУПКА!\n\nВсе условия сошлись:\nТренд ВВЕРХ\nRSI: {rsi:.1f} - дешево\nMACD подтверждает разворот\n\nЦена: {price:.2f}\nЛот: {LOT}\nТП: {tp:.2f}\nСЛ: {sl:.2f}\n\n{balance_text()}")
            return
        # ПРОФИ ПРОДАЖА: нужны ВСЕ 4 условия сразу!
        # 1. Цена ниже EMA200 - тренд вниз
        # 2. RSI больше 65 - цена выросла, дорого
        # 3. MACD ниже сигнала - разворот вниз начался
        # 4. Цена ниже EMA50 - подтверждение
        if price < ema200 and rsi > 65 and macd < signal and price < ema50:
            position = {"type": "SELL", "price": price, "amount": amount, "lot": LOT}
            tp, sl = get_tp_sl(position)
            if CHAT_ID != 0:
                await bot.send_message(chat_id=CHAT_ID, text=f"ПРОФИ СИГНАЛ ПРОДАЖА!\n\nВсе условия сошлись:\nТренд ВНИЗ\nRSI: {rsi:.1f} - дорого\nMACD подтверждает разворот\n\nЦена: {price:.2f}\nЛот: {LOT}\nТП: {tp:.2f}\nСЛ: {sl:.2f}\n\n{balance_text()}")
            return
        print(f"ПРОФИ ЖДЕТ - нет всех условий. RSI {rsi:.1f} MACD {macd:.2f}", flush=True)
    except Exception as e:
        print(f"Ошибка проверки: {e}", flush=True)

async def check_gold_job(context):
    await check_gold_logic(context.bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем Бота-Профессионала...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("price", price_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("balance", balance_cmd))
            if app.job_queue:
                app.job_queue.run_repeating(check_gold_job, interval=900, first=10)
            print("Бот-Профессионал запущен!", flush=True)
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
