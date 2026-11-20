import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"

def get_gold_signal():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=5d&interval=1h"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()
        result = data['chart']['result'][0]
        closes = [x for x in result['indicators']['quote'][0]['close'] if x is not None]
        price = closes[-1]

        gains = []
        losses = []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 1
        avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 1
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        ma20 = sum(closes[-20:]) / min(20, len(closes))

        score = 0
        if price > ma20:
            score += 3
        else:
            score -= 3
        if rsi < 35:
            score += 4
        elif rsi < 50:
            score += 1
        elif rsi > 65:
            score -= 4
        elif rsi > 50:
            score -= 1

        if score >= 4:
            signal = "BUY 🟢 ПОКУПКА"
            strength = min(10, 5 + score)
        elif score <= -4:
            signal = "SELL 🔴 ПРОДАЖА"
            strength = min(10, 5 + abs(score))
        else:
            signal = "WAIT 🟡 ЖДАТЬ"
            strength = 3

        if strength >= 7:
            strength_text = "СИЛЬНЫЙ 💪"
        elif strength >= 5:
            strength_text = "СРЕДНИЙ 👍"
        else:
            strength_text = "СЛАБЫЙ 👎"

        return f"""🥇 ЗОЛОТО XAU/USD

💰 Цена: {price:.2f} $
📊 RSI: {rsi:.1f}
📈 MA20: {ma20:.2f} $

🎯 Сигнал: {signal}
⚡ Сила: {strength}/10 - {strength_text}

🛑 Стоп: {price*0.998:.2f}
✅ Тейк: {price*1.004:.2f}

⚠️ Только индикатор, не финансовый совет."""
    except Exception as e:
        return f"Ошибка: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🥇 Сигнал по Золоту", callback_data="gold")],
        [InlineKeyboardButton("🔥 Попробуйте Бесплатно", callback_data="trial")]
    ]
    await update.message.reply_text("НОВЫЙ БОТ ДЛЯ ПРОБИВА\n\nВыбери:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "gold":
        await query.message.reply_text("⏳ Считаю сигнал по золоту...")
        await query.message.reply_text(get_gold_signal())
    elif query.data == "trial":
        await query.message.reply_text("Бесплатная проба активирована ✅")

async def gold_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Считаю сигнал по золоту...")
    await update.message.reply_text(get_gold_signal())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold_cmd))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
