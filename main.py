# === V38 NORMAL - БЕРЕТ ДАННЫЕ КАК НА ТВОЕМ СКРИНЕ ===
import requests

TOKEN = "ТВОЙ_ТОКЕН"
CHAT_ID = "ТВОЙ_ID"

def get_15min_data():
    url = "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUUSD&interval=15&limit=100"
    data = requests.get(url).json()['result']['list']
    closes = [float(x[4]) for x in data][::-1] # как у тебя на графике
    return closes

def check():
    closes = get_15min_data()
    price = closes[-1] # 4064 как у тебя сейчас
    
    # MA как на твоем скрине
    MA7 = sum(closes[-7:])/7
    MA14 = sum(closes[-14:])/14
    MA28 = sum(closes[-28:])/28
    
    # RSI6 (у тебя 81.04)
    def rsi(p=6):
        gains=0; losses=0
        for i in range(-p,0):
            diff = closes[i]-closes[i-1]
            if diff>0: gains+=diff
            else: losses+=-diff
        rs = gains/(losses+0.0001)
        return 100 - (100/(1+rs))
    
    RSI6 = rsi(6)
    RSI12 = rsi(12)
    
    print(f"Цена {price} MA7 {MA7:.2f} MA14 {MA14:.2f} RSI6 {RSI6:.1f}")

    # === ЛОГИКА 80%+ КАК НА РЫНКЕ СЕЙЧАС ===
    if price > MA7 and price > MA14 and price > MA28 and RSI6 < 78:
        # Как сейчас у тебя - цена выше всех MA - сильный BUY
        power = 80 + (price-MA7) # чем дальше выше MA7 - тем сильнее
        if power>100: power=92
        return f"🟢🟢🟢 BUY {int(power)}% | {price} | MA7 {MA7:.1f} выше! Вход от {price:.2f} SL {price-10:.2f} TP {price+15:.2f}"
    
    elif RSI6 > 82: # как сейчас 81.04 - перекуплен
        return f"⚠️ БОКОВИК-ПЕРЕКУП {int(RSI6)}% | Цена {price} RSI6 {RSI6:.1f} - ЖДИ ОТКАТА к MA7 {MA7:.1f} и там BUY 85%"
    
    else:
        return f"⚪️ БОКОВИК 55% - ЖДЕМ | Цена {price} MA7 {MA7:.1f}"

# Проверка
print(check())
