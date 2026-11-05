import os, io
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("!!! NO BOT_TOKEN, using dummy to keep app alive")
    TOKEN = "1234567890:AAH_dummy_token_for_render"

try:
    bot = telebot.TeleBot(TOKEN)
except Exception as e:
    print("Bot init failed:", e)
    bot = telebot.TeleBot("1234567890:AAH_dummy_token_for_render")

app = Flask(__name__)

def make_signal():
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12,12,W-12,H-12], outline=(212,175,55), width=8)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
    except:
        f1 = ImageFont.load_default()
        f2 = ImageFont.load_default()
    draw.text((W//2, 400), "SUHOY - XAUUSD", fill=(212,175,55), font=f1, anchor="
