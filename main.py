import os
import io
import json
import time
import random
import threading
import requests
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_FILE = '/tmp/chats.json'
SIGNAL_FILE = '/tmp/signals.json'

def load_json(path, default):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f)
    except:
        pass

def get_price():
    try:
        r = requests.get('https://api.gold-api.com/price/XAU', timeout=4).json()
        return round(float(r['price']), 2)
    except:
        return round(4128.7
