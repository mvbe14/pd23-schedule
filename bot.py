# bot.py

import logging
from datetime import date, timedelta, datetime

from telebot import TeleBot, types

from config import BOT_TOKEN, WEBAPP_URL, GROUP_TITLE
from schedule_data import get_schedule_for_date, format_day_schedule_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN, parse_mode="HTML")


def build_main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📆 Сьогодні", "➡️ Завтра")

    # Кнопка WebApp працює ТІЛЬКИ якщо WEBAPP_URL вказує на реальний HTTPS-сайт
    if WEBAPP_URL:
        webapp_button = types.KeyboardButton(
            text="🌐 Веб-розклад",
            web_app=types.WebAppInfo(url=WEBAPP_URL),
        )
        kb.row(webapp_button)

    return kb


@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    text = (
        f"Привіт, {message.from_user.first_name}!\n\n"
        f"Це бот-розклад для групи <b>{GROUP_TITLE}</b>.\n\n"
        "Що я вмію:\n"
        "• показати розклад на сьогодні → /today або кнопка «📆 Сьогодні»\n"
        "• показати розклад на завтра → /tomorrow або кнопка «➡️ Завтра»\n"
        "• показати розклад на дату → /date YYYY-MM-DD\n"
    )
    if WEBAPP_URL:
        text += "• відкрити гарний веб-розклад → кнопка «🌐 Веб-розклад»\n"

    bot.send_message(message.chat.id, text, reply_markup=build_main_keyboard())


@bot.message_handler(commands=["today"])
def cmd_today(message):
    d = date.today()
    lessons = get_schedule_for_date(d)
    text = format_day_schedule_text(lessons, day=d)
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["tomorrow"])
def cmd_tomorrow(message):
    d = date.today() + timedelta(days=1)
    lessons = get_schedule_for_date(d)
    text = format_day_schedule_text(lessons, day=d)
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["date"])
def cmd_date(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message,
            "Використання: /date YYYY-MM-DD\nНаприклад: /date 2025-12-01",
        )
        return

    try:
        d = datetime.fromisoformat(parts[1]).date()
    except ValueError:
        bot.reply_to(
            message,
            "Невірний формат дати. Використай YYYY-MM-DD, наприклад /date 2025-12-01",
        )
        return

    lessons = get_schedule_for_date(d)
    text = format_day_schedule_text(lessons, day=d)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    txt = message.text.strip()
    if txt == "📆 Сьогодні":
        cmd_today(message)
    elif txt == "➡️ Завтра":
        cmd_tomorrow(message)
    else:
        bot.reply_to(
            message,
            "Я тебе не зрозумів 😅\n"
            "Спробуй /today, /tomorrow або /date YYYY-MM-DD.",
        )


if __name__ == "__main__":
    logger.info("Бот запущений…")
    bot.infinity_polling(skip_pending=True)
