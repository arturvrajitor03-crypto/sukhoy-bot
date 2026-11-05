import os, requests, random, threading, time
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)
active_trades = {}

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        price = float(r.get("price", 0))
        if price > 1000:
            return int(price)
    except:
        pass
    return 4077

def analyze_market(price):
    if price >= 4050:
        direction = "BUY"
        entry = f"выше {price}"
        sl = price - 9
        tp1 = price + 4
        tp2 = price + 8
        tp3 = price + 13
    else:
        direction = "SELL"
        entry = f"ниже {price}"
        sl = price + 9
        tp1 = price - 4
        tp2 = price - 8
        tp3 = price - 13
    return direction, entry, sl, tp1, tp2, tp3, price

def find_template():
    for f in os.listdir("."):
        if f.lower().endswith((".jpg",".jpeg",".png",".webp")):
            if "main" not in f.lower():
                return f
    return None

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def create_signal_image(template_path, direction, entry, sl, tp1, tp2, tp3, hit_tps):
    base = Image.open(template_path).convert("RGB").resize((1200, 1900))
    draw = ImageDraw.Draw(base)
    font_big = get_font(82)
    font_mid = get_font(50)
    color_dir = (255, 30, 30) if direction == "SELL" else (0, 255, 90)
    draw.rectangle([0, 520, 1200, 670], fill=(0,0,0))
    text_dir = f"XAUUSD - {direction}"
    bbox = draw.textbbox((0,0), text_dir, font=font_big)
    w = bbox[2]-bbox[0]
    draw.text(((1200-w)//2, 550), text_dir, font=font_big, fill=color_dir)
    draw.rectangle([130, 1330, 1070, 1740], fill=(0,0,0))
    draw.rectangle([130, 1330, 1070, 1740], outline=(212,175,55), width=2)
    tp1_mark = "✅" if 1 in hit_tps else "⬜"
    tp2_mark = "✅" if 2 in hit_tps else "⬜"
    tp3_mark = "✅" if 3 in hit_tps else "⬜"
    lines = [f"Вход: {entry}", f"SL: {sl}", f"TP1: {tp1}  {tp1_mark}", f"TP2: {tp2}  {tp2_mark}", f"TP3: {tp3}  {tp3_mark}"]
    y = 1345
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_mid)
        w = bbox[2]-bbox[0]
        draw.text(((1200-w)//2, y), line, font=font_mid, fill=(255,235,180))
        y += 70
    output_path = f"/tmp/signal_{random.randint(1,99999)}.jpg"
    base.save(output_path, quality=95)
    return output_path

def send_photo(chat_id, photo_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
        requests.post(url, data=data, files=files, timeout=25)

def send_text(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)

def check_tps_loop():
    while True:
        time.sleep(60)
        if not active_trades: continue
        try:
            current_price = get_gold_price()
            for chat_id in list(active_trades.keys()):
                trade = active_trades.get(chat_id)
                if not trade: continue
                direction, tp1, tp2, tp3 = trade['direction'], trade['tp1'], trade['tp2'], trade['tp3']
                hit = trade['hit_tp']
                new_hit = []
                if direction == "SELL":
                    if current_price <= tp1 and 1 not in hit: new_hit.append(1)
                    if current_price <= tp2 and 2 not in hit: new_hit.append(2)
                    if current_price <= tp3 and 3 not in hit: new_hit.append(3)
                else:
                    if current_price >= tp1 and 1 not in hit: new_hit.append(1)
                    if current_price >= tp2 and 2 not in hit: new_hit.append(2)
                    if current_price >= tp3 and 3 not in hit: new_hit.append(3)
                for tp_num in new_hit:
                    hit.append(tp_num)
                    tpl = find_template()
                    if tpl:
                        img = create_signal_image(tpl, direction, trade['entry'], trade['sl'], tp1, tp2, tp3, hit)
                        send_photo(chat_id, img, f"✅ TP{tp_num} ДОСТИГНУТ! Цена {current_price}$")
                if len(hit) >= 3:
                    send_text(chat_id, "🎉 ВСЕ ТП ДОСТИГНУТЫ!")
                    active_trades.pop(chat_id, None)
        except: time.sleep(5)

threading.Thread(target=check_tps_loop, daemon=True).start()

# АВТО-УСТАНОВКА WEBHOOK - ЧТОБЫ ПРИНИМАЛ КОМАНДЫ
def set_webhook():
    time.sleep(3)
    try:
        # Render сам дает URL
        base_url = os.getenv("RENDER_EXTERNAL_URL")
        if base_url:
            webhook_url = f"{base_url}/webhook"
            requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}", timeout=10)
            print(f"Webhook set to {webhook_url}")
    except Exception as e:
        print(f"Webhook err {e}")

threading.Thread(target=set_webhook, daemon=True).start()

@app.route('/')
def home():
    return "SUHOY LIVE - ACCEPTING"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"].strip()
            if text == "/start":
                send_text(chat_id, "👑 СУХОЙ ПРИНИМАЕТ!\n\n/dry - сигнал\n/stop - стоп\n/price - цена")
            elif text == "/stop":
                active_trades.pop(chat_id, None)
                send_text(chat_id, "🛑 Стоп")
            elif text.startswith("/dry"):
                price = get_gold_price()
                direction, entry, sl, tp1, tp2, tp3, real_price = analyze_market(price)
                tpl = find_template()
                if not tpl:
                    send_text(chat_id, "❌ Загрузи шаблон JPG в репо!")
                    return "ok"
                active_trades[chat_id] = {'direction': direction, 'entry': entry, 'sl': sl, 'tp1': tp1, 'tp2': tp2, 'tp3': tp3, 'hit_tp': []}
                img = create_signal_image(tpl, direction, entry, sl, tp1, tp2, tp3, [])
                caption = f"👑 {direction} {int(real_price)}$\nTP1 {tp1} ⬜\nTP2 {tp2} ⬜\nTP3 {tp3} ⬜\nСлежу и ставлю ✅"
                send_photo(chat_id, img, caption)
            elif text == "/price":
                send_text(chat_id, f"💰 {get_gold_price()}$")
    except Exception as e:
        print(f"ERR {e}")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
