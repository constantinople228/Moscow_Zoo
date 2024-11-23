import telebot
import re
from telebot import types
from config import TOKEN, QuestionsAboutAnimals, totem_info, program_info

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    photo = open('MZoo-logo-hor-universal-rus-preview-RGB.jpg', 'rb')
    bot.send_photo(message.chat.id, photo, caption=f'Приветствую, {message.chat.username}! Вы попал на викторину, связанную с Московским зоопарком, \
на тему "Какое у вас тотемное животное?". \n\nГотовы? Тогда нажми на кнопку ниже – "Начать тест".')
    button_start(message)


@bot.message_handler(commands=['button'])
def button_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("Начать тест")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Вот там  ⬇️', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.lower() == 'начать тест' or message.text.lower() == 'связаться с сотрудником зоопарка' or message.text.lower() == 'сыграть снова' or message.text.lower() == 'закончить игру' or message.text.lower() == 'перейти на официальный сайт московского зоопарка' or message.text.lower() == 'расскажите мне о программе опеки')
def handle_text(message):
    try:
        if message.text.lower() == 'начать тест' or message.text.lower() == 'сыграть снова':
            ask_question(message)
        elif message.text.lower() == 'связаться с сотрудником зоопарка':
            contact_zoo_staff(message)
        elif message.text.lower() == 'перейти на официальный сайт московского зоопарка':
            MoskowZooSite(message)
        elif message.text.lower() == 'закончить игру':
            end_game(message)
        elif message.text.lower() == 'расскажите мне о программе опеки':
            guardianship_program(message)
    except InputException as e:
        bot.reply_to(message, f"Ошибка отправки сообщения: \n{e}")


def contact_zoo_staff(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт московского зоопарка", url="https://moscowzoo.ru/contacts")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, """Для связаться с сотрудником зоопарка:
    Для справок
     +7 (499) 252-29-51
     
    Заказ экскурсий
    +7 (499) 255-53-75
    education@moscowzoo.ru

    Для болшей информации можете перейти на наш сайт⬇️
    """, reply_markup=keyboard)


def output_question_and_answers(message, k):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for var in list(QuestionsAboutAnimals.items())[k][1]:
        buttons.append(types.KeyboardButton(text=var))
    keyboard.add(*buttons)

    return keyboard


def ask_question(message: types.Message, k=-2, counts=None):
    if counts is None:
        counts = {'1': 0, '2': 0, '3': 0, '4': 0}
    if k != len(QuestionsAboutAnimals) - 2:
        k += 1
        kb = output_question_and_answers(message, k)
        msg = bot.send_message(message.chat.id, text=list(QuestionsAboutAnimals.items())[k][0], reply_markup=kb)
        bot.register_next_step_handler(msg, process_answer, k, counts)
    else:
        bot.send_message(message.chat.id, text='Тест завершён! 🥳\n\nИиии, Ваше тотемное животное...', reply_markup=types.ReplyKeyboardRemove())
        calculation_results(counts, message)


@bot.message_handler()
def process_answer(message: types.Message, k, counts):
    try:
        if re.search(r'^([1-4]\.\s)', message.text):
            counts[message.text[0]] += 1
            ask_question(message, k, counts)
        else:
            raise InputException("– Нажимайте на кнопки ниже, для того, чтобы дать ответ!")
    except InputException as e:
        bot.reply_to(message, f"Ошибка отправки сообщения: \n{e}")
        ask_question(message, k-1, counts)

    print(counts)


def calculation_results(counts, message):
    max_count = max(counts.values())
    max_categories = [cat for cat, count in counts.items() if count == max_count]

    if len(max_categories) == 1:
        bot.send_message(message.chat.id, totem_info[str(max_categories[0])])
        bot.send_sticker(message.chat.id, list(totem_info.values())[int(max_categories[0]) - 1][1])
        final_choice(message)
    else:
        bot.send_message(message.chat.id, totem_info[tuple(sorted(max_categories))])
        bot.send_sticker(message.chat.id, totem_info[tuple(sorted(max_categories))][1])
        final_choice(message)


def final_choice(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    button1 = types.KeyboardButton("Связаться с сотрудником зоопарка")
    button2 = types.KeyboardButton("Перейти на официальный сайт Московского Зоопарка")
    button3 = types.KeyboardButton("Расскажите мне о программе опеки")
    button4 = types.KeyboardButton("Сыграть снова")
    button5 = types.KeyboardButton("Закончить игру")

    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5)

    bot.send_message(message.chat.id, 'Выберите то, что вам нужно, нажав по кнопке ниже⬇️', reply_markup=markup)


def MoskowZooSite(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт московского зоопарка", url="https://moscowzoo.ru")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "↓ Вы можете перейти на сайт зоопарка, нажав по кнопке ниже:", reply_markup=keyboard)


@bot.message_handler()
def guardianship_program(message):
    photo2 = open('program_info.jpeg', 'rb')
    bot.send_photo(message.chat.id, photo2)
    bot.send_message(message.chat.id, program_info)


def end_game(message):
    bot.send_message(message.chat.id, "Отлично сыграли! \n\n Переходите на сайт зоопарка, для получения большей информации о животных и экскурсиях в нашем зоопарке, по ссылке:\nhttps://moscowzoo.ru")
    bot.stop_bot()


if __name__ == '__main__':
    bot.infinity_polling()
