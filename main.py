import os, requests, threading, time, random
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        p = float(r.get("price", 0))
        if p > 1000: return int(p)
    except: pass
    return 4093

def get_font(size, bold=False):
    try:
        # пробуем найти шрифт с поддержкой кириллицы
        names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "arial.ttf"] if bold else ["DejaVuSans.ttf", "arial.ttf"]
        for n in names:
            try:
                return ImageFont.truetype(n, size)
            except: continue
        # поиск в системе
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def create_image(direction, entry, sl, tp1, tp2, tp3):
    # Используем твой шаблон если есть
    if os.path.exists("template.jpg"):
        img = Image.open("template.jpg").convert("RGB")
        img = img.resize((1000, 1400))
    else:
        img = Image.new("RGB", (1000, 1400), (12, 12, 12))
    
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Цвета
    gold = (212, 175, 55)
    green = (0, 200, 80)
    red = (230, 60, 60)

    # Текст сверху
    font_title = get_font(58, True)
    font_pair = get_font(52, True)
    font_data = get_font(38, True)
    font_small = get_font(34, True)

    # Заголовок СУХОЙ - XAUUSD
    draw.text((W//2, 90), "СУХОЙ - XAUUSD", font=font_title, fill=gold, anchor="mm")

    # Направление BUY/SELL
    col = green if direction == "BUY" else red
    draw.text((W//2, 210), f"XAUUSD - {direction}", font=font_pair, fill=col, anchor="mm")

    # Круг посередине - просто золотой круг без эмодзи
    cx, cy = W//2, 500
    draw.ellipse((cx-140, cy-140, cx+140, cy+140), fill=gold, outline=(255,215,100), width=4)
    # Стрелка внутри кружка текстом
    arrow = "BUY" if direction == "BUY" else "SELL"
    font_arrow = get_font(70, True)
    draw.text((cx, cy), arrow, font=font_arrow, fill=(0,0,0), anchor="mm")

    # Прямоугольник с данными
    y0 = 750
    # рамка
    draw.rectangle((80, y0, W-80, y0+320), outline=gold, width=2)
    draw.text((W//2, y0+40), f"Вход: выше {entry}", font=font_data, fill=(240,230,180), anchor="mm")
    draw.text((W//2, y0+90), f"SL: {sl}", font=font_data, fill=(240,230,180), anchor="mm")
    draw.text((W//2, y0+140), f"TP1: {tp1}", font=font_data, fill=(240,230,180), anchor="mm")
    draw.text((W//2, y0+190), f"TP2: {tp2}", font=font_data, fill=(240,230,180), anchor="mm")
    draw.text((W//2, y0+240), f"TP3: {tp3}", font=font_data, fill=(240,230,180), anchor="mm")

    # нижняя линия
    draw.text((W//2, H-80), "t.me/твой_канал", font=font_small, fill=gold, anchor="mm")

    path = "/tmp/signal.jpg"
    img.save(path, quality=95)
    return path

def send_signal(chat_id, direction):
    price = get_gold_price()
    entry = price + random.randint(2,5) if direction=="BUY" else price - random.randint(2,5)
    sl = entry - 9 if direction=="BUY" else entry + 9
    tp1, tp2, tp3 = entry+4, entry+8, entry+13
    if direction=="SELL":
        tp1, tp2, tp3 = entry-4, entry-8, entry-13

    img_path = create_image(direction, entry, sl, tp1, tp2, tp3)
    
    text = f"👑 {direction} {entry}$\nTP1 {tp1}\nTP2 {tp2}\nTP3 {tp3}\nСлежу и ставлю ✅"
    
    with open(img_path, "rb") as f:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": chat_id, "caption": text}, files={"photo": f})

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        txt = data["message"].get("text","")
        if txt in ["/start", "/dry"]:
            if txt == "/start":
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "👑 СУХОЙ с картинками!\n/dry - сигнал"})
            else:
                direction = random.choice(["BUY", "SELL"])
                threading.Thread(target=send_signal, args=(chat_id, direction)).start()
    return "ok"

@app.route("/")
def home():
    return "Bot alive"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
