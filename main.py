import threading
import time

CHANNEL_ID = "@ТВОЙ_КАНАЛ"  # или ID чата куда слать, например -100123456789
# Если хочешь чтобы слал тебе в личку, оставь свой chat_id

def auto_sender():
    while True:
        try:
            # Ждем от 30 до 90 минут
            time.sleep(random.randint(1800, 5400))
            price = get_price()
            direction = random.choice(["BUY", "SELL"])
            
            # Простая логика "точки входа" - сейчас рандом, потом подключим RSI
            # Например, только если волатильность хорошая
            if random.random() > 0.3:  # 70% шанс отправить
                img = make_signal(price, direction)
                # Отправь в канал или себе
                try:
                    bot.send_photo(CHANNEL_ID, img, caption=f"🔥 АВТО СИГНАЛ {direction} {price}")
                except:
                    print("Не могу отправить в канал, проверь CHANNEL_ID")
        except Exception as e:
            print(f"Auto error: {e}")
            time.sleep(60)

# Запускаем авто-бота в фоне
threading.Thread(target=auto_sender, daemon=True).start()
