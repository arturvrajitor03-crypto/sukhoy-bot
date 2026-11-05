import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_real_gold():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        klines = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(k[4]) for k in klines]
        gains = 0
        losses = 0
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0:
                gains += diff
            else:
                losses += abs(diff)
        avg_gain = gains / 14
        avg_loss = losses / 14
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        return price, rsi
    except Exception as e:
        print("ERR:", e)
        return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇷🇺 СУХОЙ V5 РЕАЛЬНЫЙ - ГОТОВ! Напиши /check")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price, rsi = get_real_gold()
    if price is None:
        await update.message.reply_text("Ошибка Binance, еще раз /check")
        return
    if rsi < 30:
        txt = f"🔴 ПЕРЕПРОДАН! RSI {rsi:.1f}\nЦена {price:.2f}\n✅ ПОКУПКА 95%!"
    elif rsi < 45:
        txt = f"📉 ПАДЕНИЕ RSI {rsi:.1f} Цена {price:.2f}\nПРОДАЖА 88%"
    elif rsi > 70:
        txt = f"🟢 ПЕРЕКУПЛЕН RSI {rsi:.1f} Цена {price:.2f}\nПРОДАЖА 95%!"
    else:
        txt = f"⏸️ БОКОВИК RSI {rsi:.1f} Цена {price:.2f}"
    await update.message.reply_text(f"V5 РЕАЛЬНЫЙ:\n{txt}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.run_polling()
