import os, io, requests, random, threading, time, json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("NO BOT_TOKEN SET!")
    # Не падаем, чтобы Render не рестартовал
    TOKEN = "123:TEST"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = "/tmp/chats.json"
SIGNAL_FILE = "/tmp/signals.json"
last_prices = []
last_signal = 0

def load_chats():
    try:
        with open(CHAT_FILE, 'r') as f: return set(json.load(f))
    except: return set()
def save_chats(c):
    try:
        with open(CHAT_FILE, 'w') as f: json.dump(list(c), f)
    except: pass
def load_signals():
    try:
       
