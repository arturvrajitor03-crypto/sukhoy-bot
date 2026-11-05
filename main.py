import os
from flask import Flask, request
import telebot
from PIL import Image
import io

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def make_suhoy(user_bytes):
    # Используем твой template.jpg который уже в репозитории
    try:
        frame = Image.open("template.jpg").convert("RGB")
    except:
        frame = Image.open("frame.jpg").convert("RGB")
        
    user_img = Image.open(io.BytesIO(user_bytes)).convert("RGB")

    W, H = frame.size
    left = int(W * 0.08)
    top = int(H * 0.42)
    right = int(W * 0.92)
    bottom = int(H * 0.88)
    
    box_w = right - left
    box_h = bottom - top
    
    user_img.thumbnail((box_w, box_h), Image.LANCZOS)
    
    result = frame.copy()
    x = left + (box_w - user_img.width)//2
    y = top + (box_h - user_img.height)//2
    result.paste(user_img, (x, y))
    
    out = io.BytesIO()
    result.save(out, format='JPEG', quality=95)
    out.seek(0)
    return out

@bot.message_handler(commands=['start','dry'])
def start(m):
    bot.send_message(m.chat.id, "👑 СУХОЙ - XAUUSD на связи!\nКидай фото одежды - упакую в золото 🐂")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    bot.send_message(m.chat.id, "Сушу в золоте... ⏳")
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        res = make_suhoy(data)
        bot.send_photo(m.chat.id, res, caption="СУХОЙ - XAUUSD ✅ Готово! 👑")
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка: {e}")

@app.route('/')
def home():
    return "Live", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
