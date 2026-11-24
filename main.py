import os, threading, asyncio, time, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_ID = int(os.getenv("CHAT_ID", "0") or "0")
PORT = int(os.getenv("PORT", "10000"))
MY_PHONE = "0549676781"
user_state = {}

KEYWORDS = ["ремонт", "покрасить", "покраска", "шпаклевка", "шпаклёвка", "собрать шкаф", "сборка мебели", "сборка", "повесить", "повесить тв", "полку", "карниз", "мастер", "ищу мастера", "нужен мастер", "нужен кто", "квартира ремонт", "комнату покрасить", "дверь", "кран", "розетка", "мебель", "ikea", "икеа", "шкаф"]
BLACKLIST = ["продам", "продаю", "отдам", "куплю", "сдаю", "аренда", "работа", "вакансия", "ищу работу"]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Hunter Bot Alive!")
    def log_message(self, *a): pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        kb = [
            [InlineKeyboardButton("🎨 Покраска комнаты - 1000 шек", callback_data="pokraska")],
            [InlineKeyboardButton("🧱 Шпаклёвка + покраска - 500 шек", callback_data="shpaklevka")],
            [InlineKeyboardButton("🪑 Сборка мебели IKEA - 400 шек", callback_data="mebel")],
            [InlineKeyboardButton("📺 Повесить ТВ / полки - 250 шек", callback_data="tv")],
            [InlineKeyboardButton("🛠 Мелкий ремонт - от 200 шек", callback_data="melkiy")],
            [InlineKeyboardButton(f"📞 ПОЗВОНИТЬ МАСТЕРУ: {MY_PHONE}", url=f"tel:+972549676781")],
            [InlineKeyboardButton("📞 Попросить чтобы мастер перезвонил", callback_data="callback")],
        ]
        await update.message.reply_text(f"🔧 Ремонт в Ришоне\n\nБыстро, аккуратно, с гарантией.\nВыбери что нужно 👇\n\nИли позвони сразу: {MY_PHONE}", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text("🔧 Бот-охотник включён! Ищу заказы на ремонт...")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "callback":
        user_state[q.from_user.id] = {"service": "📞 ПРОСИТ ПЕРЕЗВОНИТЬ"}
        await q.message.reply_text("Напиши свой номер телефона, мастер перезвонит тебе в течение 10 минут.\nПример: 054-1234567, нужно покрасить комнату")
        return
    service = {"pokraska": "🎨 Покраска комнаты", "shpaklevka": "🧱 Шпаклёвка + покраска", "mebel": "🪑 Сборка мебели IKEA", "tv": "📺 Повесить ТВ / полки", "melkiy": "🛠 Мелкий ремонт"}.get(q.data, q.data)
    user_state[q.from_user.id] = {"service": service}
    await q.message.reply_text(f"Выбрал: {service}\n\nНапиши телефон и адрес.\nПример: 054-1234567, ул. Ротшильд 12, завтра после 17:00")

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ["group", "supergroup"]:
        await hunter_check(update, context); return
    uid = update.effective_user.id
    if uid not in user_state: user_state[uid] = {"service": "🔧 Заказ без кнопки"}
    info = user_state.pop(uid)
    name = update.effective_user.first_name
    username = f"@{update.effective_user.username}" if update.effective_user.username else "нет юзера"
    await update.message.reply_text(f"✅ Принято! Мастер перезвонит тебе в течение 10 минут.\nИли ты сам можешь позвонить: {MY_PHONE}")
    if MY_ID != 0:
        await context.bot.send_message(chat_id=MY_ID, text=f"📞 ПОЗВОНИ КЛИЕНТУ СРОЧНО!\n\nУслуга: {info['service']}\nКлиент: {name} {username}\nДанные: {update.message.text}\n\n👉 Нажми на номер и позвони ему сейчас!")

async def hunter_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    for bad in BLACKLIST:
        if bad in text: return
    found = None
    for kw in KEYWORDS:
        if kw in text: found = kw; break
    if not found: return
    group_name = update.effective_chat.title or "группа"
    author = update.effective_user.first_name or ""
    username = f"@{update.effective_user.username}" if update.effective_user.username else "нет юзера"
    if MY_ID != 0:
        await context.bot.send_message(chat_id=MY_ID, text=f"🔥 НАШЁЛ ЗАКАЗ! ПОЗВОНИ!\n\nГруппа: {group_name}\nЧеловек: {author} {username}\nНашёл слово: '{found}'\n\nНаписал:\n\"{update.message.text}\"\n\n👉 ПОЗВОНИ / НАПИШИ ЕМУ ПЕРВЫМ, пока не забрали!")

async def hunter_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await hunter_check(update, context)

def run_bot():
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    while True:
        try:
            print("Запускаем БОТ-ОХОТНИК...", flush=True)
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CallbackQueryHandler(button))
            app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, hunter_group_handler))
            app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, get_text))
            print("БОТ запущен!", flush=True)
            app.run_polling(drop_pending_updates=True, stop_signals=None)
        except Exception as e:
            print(f"Упал: {e}", flush=True); traceback.print_exc(); time.sleep(10)

def main():
    if TOKEN: threading.Thread(target=run_bot, daemon=True).start()
    server = HTTPServer(("0.0.0.0", PORT), Handler); server.serve_forever()

if __name__ == "__main__": main()
