import os
import io
import requests
import random
import threading
import time
import json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = "123:TEST"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = "/tmp/chats.json"
SIGNAL_FILE = "/tmp/signals.json"
last_prices = []
last_signal = 0

def load_chats():
    try:
        with open(CHAT_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_chats(chats):
    try:
        with open(CHAT_FILE, 'w') as f:
            json.dump(list(chats), f)
    except:
        pass

def load_signals():
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_signals(sigs):
    try:
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(sigs, f)
    except:
        pass

chat_ids = load_chats()

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        data = r.json()
        return round(float(data.get('price', 4128)), 2)
    except:
        return round(4128.7 +
