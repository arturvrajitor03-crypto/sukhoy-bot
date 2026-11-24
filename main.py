import requests, time, threading, os
from bs4 import BeautifulSoup
import telebot
from flask import Flask

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
MY_ID = 8131803573
PHONE = "0549676781"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Rabotaet!"

# Работа - если есть это слово, это уже может быть заказ!
WORK = ["маляр", "покрасить", "покраска", "шпаклевка", "шпатлевание", "собрать мебель", "сборка мебели", "повесить тв", "мастер на час", "каблан", "бригада", "подряд", "субподряд", "ремонт дома", "ремонт квартиры", "отделочные", "покраска подъезда", "покрасить квартиру", "покрасить дом", "покрасить стены", "сколько стоит покрасить", "цена покраски"]

# Конкуренты и мусор - НЕ ПРИСЫЛАТЬ!
STOP_WORDS = ["предлагаю", "предлагаем", "оказываю", "оказываем", "выполняю", "выполняем", "мои услуги", "наши услуги", "перевозки", "работаем", "на связи", "гарантия сохранности", "виза", "b1", "b2", "вакансия", "вакансии", "зарплата", "ставка", "оклад", "работа в компании", "приглашаем на работу", "ищу работу", "ищу подработку", "ищу вакансию"]

seen = set()

def is_order(text):
    t = text.lower()
    if any(s in t for s in STOP_WORDS):
        return False
    # Теперь надо ТОЛЬКО одно слово про работу! Без "нужен"!
    # Если человек пишет "Покраска квартиры" - это заказ!
    has_work = any(k in t for k in WORK)
    return has_work and PHONE not in t

def check_site(name, url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        # Берем не только ссылку, а весь блок объявления!
        for a in soup.find_all("a", href=True)[:200]:
            txt = a.get_text(" ", strip=True)
            # Берем еще текст рядом с объявлением
            parent = a.parent
            if parent:
                txt2 = parent.get_text(" ", strip=True)
                if len(txt2) > len(txt):
                    txt = txt2
            if len(txt) > 20 and len(txt) < 500 and is_order(txt):
                link = a["href"]
                if not link.startswith("http"):
                    link = url + link
                if link not in seen:
                    seen.add(link)
                    if "каблан" in txt.lower() or "бригада" in txt.lower() or "подряд" in txt.lower():
                        msg = f"🏗️ КАБЛАН / БРИГАДА! БОЛЬШОЙ ЗАКАЗ!\n\n📝 {txt[:400]}\n\n🔗 {link}\n\n📞 У нас есть бригада! Звони: {PHONE}"
                    else:
                        msg = f"🔥 НАШЁЛ ЗАКАЗ!\n\n📝 {txt[:400]}\n\n🔗 {link}\n\n📞 Звони быстро: {PHONE}\n\n❓ Город и цену спроси сам!"
                    bot.send_message(MY_ID, msg)
    except Exception as e:
        print(name, "error:", e)

def hunter():
    while True:
        check_site("DoskaTV", "https://doskatv.co.il")
        check_site("IL4RU", "https://il4ru.com")
        time.sleep(300)  # проверка каждые 5 минут, было 10!

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"✅ Бот v8 РАБОТАЕТ! ЗАКАЗЫ ЕСТЬ!\n\n🔍 Теперь беру ВСЕ объявления про покраску / ремонт / бригаду\n❌ НЕ беру только конкурентов 'Предлагаю услуги' и 'Виза'\n\n📞 Твой номер: {PHONE}\n\nПроверка каждые 5 минут!")

threading.Thread(target=hunter, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
