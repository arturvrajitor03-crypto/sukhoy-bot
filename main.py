from PIL import Image, ImageDraw, ImageFont

def make_chart(df, ema_series, direction, entry, stop, tp1, tp2, tp3):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), (10, 10, 12))
    draw = ImageDraw.Draw(img)

    # Золотая рамка - внешняя
    for i in range(12):
        draw.rectangle([30+i, 280+i, W-30-i, H-120-i], outline=(212,175,55))
    # Белый центр
    draw.rectangle([90, 340, W-90, H-180], fill=(245, 245, 245))

    # Заголовок
    try:
        f_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
        f_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 78)
        f_num = ImageFont.truetype("DejaVuSans-Bold.ttf", 68)
    except:
        f_title = ImageFont.load_default()
        f_big = f_title
        f_num = f_title

    draw.text((W//2, 120), "👑 СУХОЙ • XAUUSD 👑", fill=(212,175,55), font=f_title, anchor="mm")
    draw.text((90, 220), "СУХОЙ", fill=(212,175,55), font=f_big, anchor="lm")

    # Стрелка и направление
    if direction == "BUY":
        color = (0, 150, 80)
        arrow = "▲"
        arrow_text = "BUY"
        entry_text = f"Вход: выше {entry:.2f}"
    elif direction == "SELL":
        color = (220, 20, 20)
        arrow = "▼"
        arrow_text = "SELL"
        entry_text = f"Вход: ниже {entry:.2f}"
    else:
        color = (150, 150, 150)
        arrow = "⏳"
        arrow_text = "WAIT"
        entry_text = f"Цена: {entry:.2f}"

    draw.text((W//2, 650), arrow, fill=color, font=ImageFont.truetype("DejaVuSans-Bold.ttf", 220), anchor="mm")
    draw.text((W//2, 950), f"XAUUSD — {arrow_text}", fill=(0,0,0), font=f_big, anchor="mm")

    y = 1080
    lines = [
        (entry_text, color),
        (f"SL: {stop:.2f}", color),
        (f"TP1: {tp1:.2f}", color),
        (f"TP2: {tp2:.2f}", color),
        (f"TP3: {tp3:.2f}", color),
    ]
    for txt, c in lines:
        # Черная часть до двоеточия, цветная цифры - упрощенно весь текст
        draw.text((W//2, y), txt, fill=(0,0,0), font=f_num, anchor="mm")
        y += 110

    # Низ
    draw.text((W//2, H-80), "СУХОЙ • XAUUSD", fill=(212,175,55), font=f_title, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
