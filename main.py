import os, requests
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))
position = None
entry_price = 0

def get_klines():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100"
    r = requests.get(url, timeout=10).json()
    df = pd.DataFrame(r, columns=["t","o","h","l","c","v","ct","q","n","tb","tq","ig"])
    df["c"] = df["c"].astype(float)
    df["v"] = df["v"].astype(float)
    return df

def calc(df):
    close = df["c"]
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = -delta.where(delta<0,0).rolling(14).mean()
    rsi = (100 - (100/(1+gain/loss))).iloc[-1]
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    ema200 = close.ewm(span=200).mean().iloc[-1]
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd_line = ema12-ema26
    macd = macd_line.iloc[-1]
    signal = macd_line.ewm(span=9).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]
    upper = ma20 + 2*std
    lower = ma20 - 2*std
    low14 = close.rolling(14).min().iloc[-1]
    high14 = close.rolling(14).max().iloc[-1]
    stoch = (close.iloc[-1]-low14)/(high14-low14)*100 if high14!=low14 else 50
    vol_now = df["v"].iloc[-1]
    vol_avg = df["v"].rolling(20).mean().iloc[-1]
    price = close.iloc[-1]
    return price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg

def score_system(price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg):
    score=0; reasons=[]
    if 30 <= rsi <= 75:
        score+=1; reasons.append(f"RSI {rsi:.1f} ок")
    elif rsi>75 and price>ema20 and macd>signal:
        score+=1; reasons.append(f"RSI {rsi:.1f} высокий но тренд сильный")
    if price>ema20 and price>ema50:
        score+=1; reasons.append("Выше EMA20/50")
    if price>ema200:
        score+=1; reasons.append("Выше EMA200")
    if macd>signal:
        score+=1; reasons.append("MACD +")
    if price>lower and price<upper*1.005:
        score+=1; reasons.append("Bollinger ок")
    if stoch<85 and vol_now>vol_avg*0.8:
        score+=1; reasons.append(f"Stoch {stoch:.0f} + Объем ок")
    return score, reasons

async def check_job(context: ContextTypes.DEFAULT_TYPE):
    global position, entry_price
    try:
        df = get_klines()
        price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg = calc(df)
        score, reasons = score_system(price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg)
        print(f"Price {price:.2f} RSI {rsi:.1f} Score {score}/6 Pos {position}")
        if position is None:
            if score >= 3 and price > ema20:
                position="LONG"; entry_price=price
                await context.bot.send_message(chat_id=CHAT_ID, text=f"🟢 ПОКУПКА ЗОЛОТО (АКТИВНЫЙ)\nЦена: {price:.2f} $\nСкор: {score}/6\nПричины: {', '.join(reasons)}\nRSI: {rsi:.1f} | MACD: {macd:.2f}")
        else:
            pnl=(price-entry_price)/entry_price*100
            if pnl>=1.5:
                await context.bot.send_message(chat_id=CHAT_ID, text=f"✅ ПРОДАЖА +{pnl:.2f}%\nВход: {entry_price:.2f} -> Выход: {price:.2f}")
                position=None
            elif pnl<=-0.7:
                await context.bot.send_message(chat_id=CHAT_ID, text=f"🛑 СТОП {pnl:.2f}%\nВход: {entry_price:.2f} -> Выход: {price:.2f}")
                position=None
    except Exception as e:
        print("job error", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активный запущен! 🔥 Ждём сигнал от 3/6")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df=get_klines()
    price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg = calc(df)
    score, reasons = score_system(price, rsi, ema20, ema50, ema200, macd, signal, upper, lower, stoch, vol_now, vol_avg)
    await update.message.reply_text(f"📊 ЗОЛОТО PAXG: {price:.2f} $\nRSI: {rsi:.1f}\nEMA20: {ema20:.2f} EMA50: {ema50:.2f} EMA200: {ema200:.2f}\nMACD: {macd:.2f} / {signal:.2f}\nBollinger: {lower:.2f} - {upper:.2f}\nStoch: {stoch:.1f}\nСкор: {score}/6\n{', '.join(reasons)}")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if position:
        await update.message.reply_text(f"Открыта сделка: вход {entry_price:.2f}")
    else:
        await update.message.reply_text("Нет открытых позиций. Ждём сигнал... 👀 Активный режим 3/6")

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Виртуальный баланс: 500 $")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.job_queue.run_repeating(check_job, interval=60, first=10)
    app.run_polling()

if __name__ == "__main__":
    main()
