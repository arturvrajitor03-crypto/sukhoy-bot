import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
AUTO = {"on": False}

def get_signal():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        k = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(x[4]) for x in k]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: g+=d
            else: l+=abs(d)
        rsi = 100 if l==0 else 100-(100/(1+(g/14)/(l/14)))
        ema = sum(closes[-20:])/20
        sig = "WAIT"
        if rsi<32 and price>ema: sig="BUY"
        elif rsi>68 and price<ema: sig="SELL"
        sl = price*0.998 if sig=="BUY" else price*1.002
        tp = price*1.005 if sig=="BUY" else price*0.995
        return price,rsi,sig,sl,tp
    except:
        return None,None,"ERROR",0,0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 V8 AUTO LIVE!\n/check - сигнал\n/auto_on - авто вкл\n/auto_off - авто выкл")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p,rsi,sig,sl,tp = get_signal()
    if not p:
        await update.message.reply_text("Ошибка, попробуй еще /check")
        return
    await update.message.reply_text(f"GOLD {p:.2f}\nRSI {rsi:.1f}\nSIGNAL {sig}\nSL {sl:.2f} TP {tp:.2f}\nAUTO {'ON' if AUTO['on'] else 'OFF'}")

async def auto_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AUTO["on"]=True
    await update.message.reply_text("✅ АВТО ВКЛ! Пиши /check каждые 5 мин - буду давать сигналы!")

async def auto_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AUTO["on"]=False
    await update.message.reply_text("🛑 АВТО ВЫКЛ")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("auto_on", auto_on))
app.add_handler(CommandHandler("auto_off", auto_off))
app.run_polling()
