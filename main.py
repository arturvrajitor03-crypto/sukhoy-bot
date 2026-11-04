def create_signal_image(template_path, direction, entry, sl, tp1, tp2, tp3):
    base = Image.open(template_path).convert("RGB")
    base = base.resize((1200, 1900))
    draw = ImageDraw.Draw(base)
    
    font_big = get_font(82)
    font_mid = get_font(52)
    
    color_dir = (255, 30, 30) if direction == "SELL" else (0, 255, 90)
    
    # Заголовок
    draw.rectangle([0, 520, 1200, 670], fill=(0,0,0))
    text_dir = f"XAUUSD - {direction}"
    bbox = draw.textbbox((0,0), text_dir, font=font_big)
    w = bbox[2]-bbox[0]
    draw.text(((1200-w)//2, 550), text_dir, font=font_big, fill=color_dir)
    
    # Нижний блок
    draw.rectangle([130, 1330, 1070, 1720], fill=(0,0,0))
    draw.rectangle([130, 1330, 1070, 1720], outline=(212,175,55), width=2)
    
    # С галочками после каждого ТП!
    lines = [
        f"Вход: {entry}",
        f"SL: {sl}",
        f"TP1: {tp1}  ✅",
        f"TP2: {tp2}  ✅",
        f"TP3: {tp3}  ✅"
    ]
    
    y = 1340
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_mid)
        w = bbox[2]-bbox[0]
        # Галочки делаем золотым цветом
        if "✅" in line:
            # Текст без галочки по центру
            text_part = line.replace("  ✅", "")
            bbox2 = draw.textbbox((0,0), text_part, font=font_mid)
            w2 = bbox2[2]-bbox2[0]
            draw.text(((1200-w2)//2 - 30, y), text_part, font=font_mid, fill=(255,235,180))
            # Галочку зеленым
            draw.text(((1200-w2)//2 + w2 + 10, y), "✅", font=font_mid, fill=(0,255,90))
        else:
            draw.text(((1200-w)//2, y), line, font=font_mid, fill=(255,235,180))
        y += 70
    
    output_path = "/tmp/signal.jpg"
    base.save(output_path, quality=95)
    return output_path
