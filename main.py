import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Логи чтобы видеть в Render что происходит
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

# Храним прошлую цену чтобы не спамить
last_price = 0
last_signal = ""

def get_gold_price():
    """Берем цену золота с бесплатного API"""
    r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15)
    data = r.json()
    item = data["items"][0]
    return float(item["curr"]), float(item["xauPrice"]), float(item["chg"])

def make_signal(price):
    """Простая логика сигнала"""
    global last_signal
    signal = ""
    if price >= 2700:
        signal = "🔴 ПРОДАЖА - Цена очень высоко, ждем откат вниз"
    elif price >= 2650:
        signal = "🟡 ОСТОРОЖНО - Цена высоко, не покупаем"
    elif price <= 2600:
        signal = "🟢 ПОКУПКА - Цена низко, хороший вход"
    elif price <= 2550:
        signal = "🟢🟢 СИЛЬНАЯ ПОКУПКА - Цена очень низко"
    else:
        signal = "⚪ ЖДЕМ
