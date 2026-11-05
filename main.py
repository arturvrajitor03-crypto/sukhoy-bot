import os
from flask import Flask, request
import telebot
from PIL import Image
import io
import requests

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def make_suhoy_image(user_photo_bytes):
    # Открываем золотую рамку
    try:
        frame = Image.open("frame.jpg").convert("RGB")
    except:
        # если файла нет - скачиваем твою рамку
        frame = Image.open(requests.get("https://i.imgur.com/your-frame.jpg", stream=True).raw)

    user_img = Image.open(io.BytesIO(user_photo_bytes)).convert("RGB")
    
    # Размеры черной области внутри рамки (подогнал под твой дизайн)
    W, H = frame.size  # ~ 1024x1920
    # Координаты куда вставлять фото пользователя
    left = int(W * 0.12)
    top = int(H * 0.28)
    right = int(W * 0.88)
    bottom = int(H * 0.90)
    
    box_w = right - left
    box_h = bottom - top
    
    # Вписываем фото пользователя красиво
    user_img.thumbnail((box_w, box_h), Image.LANCZOS)
    
    # Центрируем
    x_offset = left + (box_w - user_img.width) // 2
    y_offset = top + (box_h - user_img.height) // 2
    
    # Создаем копию
    result = frame.copy()
    result.paste(user_img, (x_offset, y_offset))
    
    # Сохраняем в байты
    out = io.BytesIO()
    result.save(out, format='JPEG', quality=95)
    out.seek(0)
    return out

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "👑 Я Сухой Артур на связи!\nОтправь фото - я сделаю СУХОЙ - XAUUSD стиль.\n\nКоманда: /dry + фото")

@bot.message_handler(commands=['dry'])
def dry_cmd(m):
    bot.send_message(m.chat.id, "Кидай фото, я высушу в золоте 🐂")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    bot.send_message(m.chat.id, "Сушу в золоте... ⏳")
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        result_img = make_suhoy_image(downloaded)
        bot.send_photo(m.chat.id, result_img, caption="СУХОЙ - XAUUSD 🐂👑 Готово!")
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка: {e}\nПроверь что залил frame.jpg в GitHub")

@app.route('/')
def index():
    return "Suhoy XAUUSD Bot Live", 200

@app.route(f"/{TOKEN}", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
