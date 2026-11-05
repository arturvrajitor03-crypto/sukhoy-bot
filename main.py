def make_image(side, entry):
    from PIL import ImageFont
    W,H = 1080,1350
    img = Image.new('RGB',(W,H),(14,14,14))
    d = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()

    d.rectangle([10,10,W-10,H-10], outline=(212,175,55), width=6)
    d.rectangle([0,0,W,180], fill=(212,175,55))
    d.text((40,45), "SUHOY GOLD SIGNALS", font=font_big, fill=(0,0,0))
    
    sl = entry-14 if side=="BUY" else entry+14
    tp1 = entry+9 if side=="BUY" else entry-9
    tp2 = entry+18 if side=="BUY" else entry-18
    tp3 = entry+30 if side=="BUY" else entry-30
    color_side = (50,255,130) if side=="BUY" else (255,70,70)

    d.text((60,240), f"{side} XAUUSD {round(entry,1)}", font=font_big, fill=color_side)
    d.text((60,360), f"ENTRY: {round(entry,1)}", font=font_med, fill=(
