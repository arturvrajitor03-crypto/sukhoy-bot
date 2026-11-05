import os, io, threading, time
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import requests

TOKEN = "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
CHATS = set()

def get_data():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100"
        klines = requests.get(url, timeout=10).json()
        closes = [float(k[4]) for k in klines]
        price = closes[-1]
        ema50 = sum(closes[-50:]) / 50
        gains = []
        losses = []
        for i in range(1,len(closes)):
            diff = closes[i]-closes[i-1]
            if diff>0
