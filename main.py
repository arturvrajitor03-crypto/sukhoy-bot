import requests, time, re
from bs4 import BeautifulSoup
import telebot

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
MY_ID = 8131803573
bot = telebot.TeleBot(TOKEN)

# === ВЕСЬ ЦЕНТР ===
CITIES = ["ришон", "холон", "бат-ям", "бат ям", "тель-авив", "тель авив",
"рамат-ган", "петах-тиква", "реховот", "нес-циона", "лод", "рамле",
"беэр-яаков", "ашдод", "центр", "мерказ"]

# === ЧТО ИЩЕМ ===
KEYWORDS = ["нужен маляр", "нужен мастер", "ищу маляра", "ищу мастера",
"покрасить", "покраска", "шпаклевка", "шпаклёвка",
"собрать мебель", "сборка мебели", "сборка икеа", "икеа",
"повесить тв", "повесить телевизор", "повесить полку",
"мастер на час", "мелкий ремонт", "нужен человек"]

PHONE = "0549676781"
seen = set()

def is_order(text):
    text = text.lower()
    # есть город центра?
    has_city = any(c in text for c in CITIES)
    # есть работа?
    has_work = any(k in text for k in KEYWORDS)
    # не наша же реклама?
    is_not_mine = PHONE not in text
    return has_city and has_work and is_not_mine

def check_doskatv():
    try:
        url = "https://doskatv.co.il"
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:100]:
            txt = a.get_text(" ", strip=True)
            if len(txt) > 20 and is_order(txt):
                link = a["href"]
                if not link.startswith("http"):
                    link = url + link
                if link not in seen:
                    seen.add(link)
                    bot.send_message(MY_ID, f"🔥 НАШЁЛ ЗАКАЗ НА DOSKATV!\n\n📝 {txt}\n\n🔗 {link}\n\n📞 Звони быстро! Твой номер для клиентов: {PHONE}")
    except Exception as e:
        print("DoskaTV error:", e)

def check_il4ru():
    try:
        url = "https://il4ru.com"
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:100]:
            txt = a.get_text(" ", strip=True)
            if len(txt) > 20 and is_order(txt):
                link = a["href"]
                if not link.startswith("http"):
                    link = url + link
                if link not in seen:
                    seen.add(link)
                    bot.send_message(MY_ID, f"🔥 НАШЁЛ ЗАКАЗ НА IL4RU!\n\n📝 {txt}\n\n🔗 {link}\n\n📞 Звони быстро!")
    except Exception as e:
        print("IL4RU error:", e)

# === ГЛАВНЫЙ ЦИКЛ - ПРОВЕРЯЕТ КАЖДЫЕ 10 МИНУТ ===
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"✅ Бот-Охотник ВКЛЮЧЁН!\n\n📍 Ищу по всему центру: Ришон, Холон, Бат-Ям, Тель-Авив, Реховот и ещё 7 городов\n🔍 Проверяю DoskaTV + IL4RU каждые 10 минут\n📞 Твой номер: {PHONE}\n\nКак только найду заказ - сразу пришлю тебе!")

print("Бот запущен - ищу по всему центру...")
while True:
    check_doskatv()
    check_il4ru()
    time.sleep(600)  # 10 минут
    try:
        bot.polling(none_stop=True, timeout=5)
    except:
        pass
