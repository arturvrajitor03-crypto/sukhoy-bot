import os, io, random, threading, time, json
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

def load_chats():
    try:
        f = open(CHAT_FILE, 'r')
        data = json.load(f)
        f.close()
        return set(data)
    except:
        return set()

def save_chats(chats):
    try:
        f = open(CHAT_FILE, 'w')
        json.dump(list(chats), f)
        f.close()
    except:
        pass

def load_signals():
    try:
        f = open(SIGNAL_FILE, 'r')
        data = json.load(f)
        f.close()
        return data
    except:
        return []

def save_signals(sigs):
    try:
        f = open(SIGNAL_FILE, 'w')
        json.dump(sigs, f)
        f.close()
    except:
        pass

chat_ids = load_chats()

def get_price():
    base = 4128.7
    delta = random.uniform(-2, 2)
    price = base + delta
    price = round(price, 2)
    return price

def get_font(size, bold):
