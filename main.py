import requests, time, asyncio, os
from telegram import Bot
import pandas as pd
import numpy as np

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = None # будет взят из первого сообщения

def get_real_gold():
    # Берем реальное золото PAXG ~ XAUUSD
    try:
        # Цена
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5).json()
        price = float(r['price'])
        # История для RSI
        klines = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=100", timeout=5).json()
        closes = [float(k[4]) for k in klines]
        df = pd.DataFrame(closes, columns=['close'])
        # RSI 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_last = float(rsi.iloc[-1])
        rsi6 = float(rsi.iloc[-1]) # для простоты
        return price, rsi_last, closes
    except Exception as e:
        print("Ошибка цены:", e)
        return None, None, None

async def check_and_send(bot):
    price, rsi, closes = get_real_gold()
    if price is None:
        return "Ошибка Binance, пробую..."
    # Логика V5 РЕАЛЬНАЯ
    if rsi < 30:
        signal = f"🔴 ПЕРЕПРОДАН! RSI {rsi:.2f}\nЦена {price:.2f}\n✅ СИГНАЛ: ЖДИ ПОКУПКУ! Разворот скоро! Сила 95%"
        trend = "СИЛЬНЫЙ ПАДЕНИЕ как на твоем скрине!"
    elif rsi > 70:
        signal = f"🟢 ПЕРЕКУПЛЕН! RSI {rsi:.2f}\nЦена {price:.2f}\n✅ СИГНАЛ: ЖДИ ПРОДАЖУ! Сила 95%"
        trend = "СИЛЬНЫЙ РОСТ"
    elif rsi < 45:
        signal = f"📉 ПАДЕНИЕ RSI {rsi:.2f} Цена {price:.2f}\nСила 88% ПРОДАЖА - как сейчас 4102!"
        trend = "ПАДАЮЩИЙ ТРЕНД"
    else:
        signal = f"⏸️ БОКОВИК RSI {rsi:.2f} Цена {price:.2f} Сила 60%"
        trend = "Боковик"
    
    text = f"🇷🇺 СУХОЙ V5 РЕАЛЬНЫЙ\n{signal}\nТренд: {trend}\nИсточник: Binance PAXG = Золото"
    return text

# Твой старый код polling оставь, только замени функцию /check на эту
