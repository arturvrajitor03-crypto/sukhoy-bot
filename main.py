import os, telebot
from flask import Flask, request
from PIL import Image
import requests
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

TEMPLATE_PATH = "template.jpg"

def make_suhoy_image(user_file):
    # Скачиваем шаблон
    template = Image.open(TEMPLATE_PATH).convert("RGB")
    W, H = template.size
    
    # Скачиваем фото юзера
    user_img = Image.open(BytesIO(user_file)).convert("RGB")
    
    # Размер вставки - в центр черной зоны (под быком)
    # Подбираем 70% ширины
    insert_w = int(W * 0.72)
    insert_h = int(H * 0.45)
    user_img = user_img.resize((insert_w, insert_h))
    
    # Вставляем чуть ниже центра
    x = (W - insert_w)//2
    y = int(H * 0.52)
    template.paste(user_img, (x, y))
    return template

@bot.message_handler(commands=['start','help'])
def start(m):
    bot.reply_to(m, "Привет! Я Сухой Артур на связи! Бот заработал ✅\n\nКоманда: /dry + фото джинс/вещи\nЯ упакую в золотой стиль СУХОЙ - XAUUSD 👑🐂")

@bot.message_handler(commands=['dry'])
def dry_cmd(m):
    bot.reply_to(m, "Кидай фото! Я засушу в золото 👑")

@bot.message_handler(content_types=['photo'])
def photo_handler(m):
    bot.send_message(m.chat.id, "Сушу фото... ⏳")
    try:
        file_id = m.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        result = make_suhoy_image(downloaded)
        
        bio = BytesIO()
        result.save(bio, 'JPEG')
        bio.seek(0)
        bot.send_photo(m.chat.id, bio, caption="СУХОЙ - XAUUSD ✅ Готово! 👑🐂")
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route('/')
def index():
    return "Bot is Live"

if __name__ == '__main__':
    app.run()
