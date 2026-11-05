import os, requests, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT = os.getenv("BOT_TOKEN")
AUTO = {"on": False, "balance": 1000.0, "pos": None} # демо баланс $1000

def get_signal():
    try:
        p = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()['price'])
        k = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=50", timeout=10).json()
        closes = [float(x[4]) for x in k]
        # RSI
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            g+=d if d>0 else 0
            l+=abs(d) if d<0 else 0
        rsi = 100 if l==0 else 100-(100/(1+g/14/(l/14)))
        # EMA 20
        ema = sum(closes[-20:])/20
        
        signal = "WAIT"
        if rsi < 32 and p > ema: signal = "BUY"
        elif rsi > 68 and p < ema: signal = "SELL"
        
        sl = p*0.998 if signal=="BUY" else p*1.002
        tp = p*1.005 if signal=="BUY" else p*0.995
        return p, rsi, signal, sl, tp, ema
    except:
        return None,None,"ERROR",0,0,0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 V8 AUTO-TRADER LIVE!\n\n"
        "/check - проверить сигнал\n"
        "/auto_on - включить авто-торговлю (ДЕМО)\n"
        "/auto_off - выключить\n"
        "/balance - мой баланс\n"
        "/pos - моя позиция\n\n"
        "Сейчас торгует ВИРТУАЛЬНО на $1000 для теста!"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p,rsi,sig,sl,tp,ema = get_signal()
    if not p:
        await update.message.reply_text("Ошибка Binance, попробуй /check еще раз")
        return
    await update.message.reply_text(
        f"💰 GOLD: {p:.2f}$\n"
        f"📊 RSI: {rsi:.1f} | EMA20: {ema:.2f}\n"
        f"🎯 СИГНАЛ: {sig}\n"
        f"🛑 SL: {sl:.2f} | ✅ TP: {tp:.2f}\n"
        f"🤖 АВТО: {'ВКЛ' if AUTO['on'] else 'ВЫКЛ'}"
    )

async def auto_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AUTO["on"] = True
    await update.message.reply_text("✅ АВТО-ТРЕЙДИНГ ВКЛ! Я буду проверять каждые 5 мин и писать тебе сделки!\n\nДЕМО режим - реальные деньги НЕ тратятся!")
    # запуск цикла
    asyncio.create_task(auto_loop(context))

async def auto_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AUTO["on"] = False
    await update.message.reply_text("🛑 АВТО ВЫКЛ")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💵 Демо баланс: ${AUTO['balance']:.2f}\nПозиция: {AUTO['pos']}")

async def pos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Позиция: {AUTO['pos'] or 'Нет открытых'}")

async def auto_loop(context):
    while AUTO["on"]:
        p,rsi,sig,sl,tp,ema = get_signal()
        if sig in ["BUY","SELL"] and AUTO["pos"] is None:
            AUTO["pos"] = f"{sig} {p:.2f} SL {sl:.2f} TP {tp:.2f}"
            # тут отправка в твой телеграм
            await context.bot.send_message(
                chat_id=list(context.application.chat_ids)[0] if hasattr(context.application,'chat_ids') else context._chat_id,
                text=f"🚀 АВТО-СДЕЛКА ОТКРЫТА!\n{sig} GOLD {p:.2f}\nSL {sl:.2f} TP {tp:.2f}\nRSI {rsi:.1f}"
            )
        await asyncio.sleep(300) # 5 мин

# Исправленный auto_loop для Render
async def auto_checker(app):
    while True:
        if AUTO["on"]:
            try:
                p,rsi,sig,sl,tp,ema = get_signal()
                if sig in ["BUY","SELL"] and AUTO["pos"] is None:
                    AUTO["pos"] = f"{sig} {p:.2f}"
                    # шлем всем кто писал боту
                    for chat_id in app.bot_data.get("chats", []):
                        await app.bot.send_message(chat_id=chat_id, text=f"🚀 V8 СИГНАЛ: {sig} GOLD {p:.2f}\nRSI {rsi:.1f}\nSL {sl:.2f} TP {tp:.2f}")
            except: pass
        await asyncio.sleep(300)

async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chats = context.bot_data.setdefault("chats", [])
    if update.effective_chat.id not in chats:
        chats.append(update.effective_chat.id)

app = Application.builder().token(BOT).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("auto_on", auto_on))
app.add_handler(CommandHandler("auto_off", auto_off))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("pos", pos))

# трекинг чатов для авто-рассылки
from telegram.ext import MessageHandler, filters
app.add_handler(MessageHandler(filters.ALL, track_chat), group=1)

# фоновый чекер
async def post_init(a):
    asyncio.create_task(auto_checker(a))

app.post_init = post_init
app.run_polling()
