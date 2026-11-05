import os
import io
import json
import time
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
        f = open(path, 'r')
        data = json.load(f)
        f.close()
        return data
    except:
        return default

def save_json(path, data):
    try:
        f = open(path, 'w')
        json.dump(data, f)
        f.close()
    except:
        pass

def get_price():
    try:
        url = 'https://api.gold-api.com/price/XAU'
        resp = requests.get(url, timeout=4)
        j =
