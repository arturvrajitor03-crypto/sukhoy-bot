import os, threading, asyncio, time, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_ID = int(os.getenv("CHAT_ID", "0") or "0")
PORT = int(os.getenv("PORT", "10000"))
user_state = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Remont Bot Alive!")
    def log_message(self, *a): pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MY_ID
    # Если это ты - запоминаем твой ID чтобы заказы приходили тебе
    # Но заказы от клиентов всё равно идут на CHAT_ID из Render
    kb = [
        [InlineKeyboardButton("🎨 Покраска комнаты - 1000 шек", callback_data="pokraska")],
        [InlineKeyboardButton("🧱 Шпаклёвка + покраска - 500 шек", callback_data="shpaklevka")],
        [InlineKeyboardButton("🪑 Сборка мебели IKEA - 400 шек", callback_data="mebel")],
        [InlineKeyboardButton("📺 Повесить ТВ / полки - 250 шек", callback_data="tv")],
        [InlineKeyboardButton("🛠 Мелкий ремонт - от 200 шек", callback_data="melkiy")],
        [InlineKeyboardButton("📞 Позвонить мастеру", callback_data="call")],
    ]
    await update.message.reply_text(
        "🔧 Ремонт в Ришоне Ле Цион\n\nБыстро, аккуратно, с гарантией.\nВыбери что нужно 👇\n\nИли напиши сразу телефон и адрес.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "call":
        await q.message.reply_text("📞 Напиши свой номер, мастер перезвонит тебе в течение 15 минут.\nПример: 054-1234567, нужно повесить ТВ")
        user_state[q.from_user.id] = {"service": "📞 Просит перезвонить"}
        return
    service = {
        "pokraska": "🎨 Покраска комнаты",
        "shpaklevka": "🧱 Шпаклёвка + покраска",
        "mebel": "🪑 Сборка мебели IKEA",
        "tv": "📺 Повесить ТВ / полки",
        "melkiy": "🛠 Мелкий ремонт"
    }.get(q.data, q.data)
    user_state[q.from_user.id] = {"service": service}
    await q.message.reply_text(
        f"Выбрал: {service}\n\nНапиши свой телефон и адрес в Ришоне.\nПример: 054-1234567, ул. Ротшильд 12, завтра после 17:00"
    )

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_state:
        # Если клиент просто написал без кнопки - тоже принимаем как заказ
        user_state[uid] = {"service": "🔧 Заказ без кнопки"}
    info = user_state.pop(uid)
    name = update.effective_user.first_name
    username = f"@{update.effective_user.username}" if update.effective_user.username else "нет юзера"
    text_client = update.message.text
    await update.message.reply_text("✅ Заказ принят! Мастер напишет тебе в течение 15 минут.\nСпасибо что выбрал нас! 🔧")
    if MY_ID != 0:
        await context.bot.send_message(
            chat_id=MY_ID,
            text=f"🔥 НОВЫЙ ЗАКАЗ РЕМОНТ!\n\nУслуга: {info['service']}\nКлиент: {name} {username}\nДанные: {text_client}\n\nОтветь ему в Telegram: {username}"
        )

def run_bot():
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем БОТ ТОЛЬКО РЕМОНТ...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CallbackQueryHandler(button))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))
            print("БОТ РЕМОНТ запущен!", flush=True)
            app.run_polling(drop_pending_updates=True, stop_signals=None)
        except Exception as e:
            print(f"Упал: {e}", flush=True); traceback.print_exc(); time.sleep(10)

def main():
    if TOKEN:
        threading.Thread(target=run_bot, daemon=True).start()
    else:
        print("ОШИБКА: Нет TELEGRAM_TOKEN!", flush=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
