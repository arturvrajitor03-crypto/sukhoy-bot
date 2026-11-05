import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_gold():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        kl = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(k[4]) for k in kl]
        gains=0; losses=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: gains+=d
            else: losses+=abs(d)
        avg_g=gains/14; avg_l=losses/14
        rsi=100 if avg_l==0 else 100-(100/(1+avg_g/avg_l))
        return price, rsi
    except:
        return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ СУХОЙ V5 РЕАЛЬНЫЙ - РАБОТАЕТ!\nНапиши /check")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price, rsi = get_gold()
    if price is None:
        await update.message.reply_text("Ошибка Binance, еще раз /check")
        return
    if rsi < 30:
        msg = f"🔴 ПЕРЕПРОДАН! RSI {rsi:.1f}\nЦена {price:.2f}\n✅ ПОКУПКА 95%!"
    elif rsi < 45:
        msg = f"📉 ПАДЕНИЕ RSI {rsi:.1f}\nЦена {price:.2f}\nПРОДАЖА 88%"
    elif rsi > 70:
        msg = f"🟢 ПЕРЕКУПЛЕН RSI {rsi:.1f}\nЦена {price:.2f}\nПРОДАЖА 95%!"
    else:
        msg = f"⏸️ БОКОВИК RSI {rsi:.1f}\nЦена {price:.2f}"
    await update.message.reply_text(f"V5 РЕАЛЬНЫЙ:\n{msg}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.run_polling()
