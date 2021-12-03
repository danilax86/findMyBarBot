import math
from math import cos, sin, asin, sqrt

import telebot
from requests.exceptions import MissingSchema
from telebot import types

from PIL import Image
import requests

import send_message
from DBManager import DataBaseManager
from config import *

# Подключаемся к боту по токену
bot = telebot.TeleBot(BOT_TOKEN, parse_mode = "MARKDOWN")  # Не использовать parse_mode="MarkdownV2" !!!

# Подключаемся к базе данных
db = DataBaseManager(db_host, db_name, db_user, db_pass)


def send_info(name, description, address, distance):
    """
    Шаблон для отправки информации о месте пользователю

    :param name: название места
    :param description: описание места
    :param address: адрес места
    :param distance: расстояние от пользователя до места
    :return:
    """

    return "*" + name + "*" + \
           "\n\n" + description + \
           "\n\n" + "📍" + address + \
           "\n\n" + "📏" + " в " + str(distance) + " км от вас"


# Создаем список мест для админки
place = [None] * 6


def process_name_step(message, context):
    """
    Получаем от админа название места и запрашиваем адрес места

    :param context: аргументы call-back функции
    :param message: сообщение
    """

    try:
        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Произошла отмена операции")
            return
        else:
            raise AttributeError
    except AttributeError:
        place[0] = message.text
        msg = bot.reply_to(message, "Введи адрес места")
        bot.register_next_step_handler(msg, process_address_step, context)


def process_description_step(message, context):
    """
    Получаем от админа описание места и запрашиваем подтверждение изменений

    :param context: аргументы call-back функции
    :param message: сообщение
    """

    try:
        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Произошла отмена операции")
            return
        else:
            raise AttributeError
    except AttributeError:

        to_edit = context[0]
        if to_edit:
            text = "Точно изменить место?"
        else:
            text = "Добавить в базу данных?"

        place[3] = message.text
        msg = bot.reply_to(message, text)
        bot.register_next_step_handler(msg, work_with_db_step, context)


def process_address_step(message, context):
    """
    Получаем от админа адрес места и запрашиваем описание места

    :param context: аргументы call-back функции
    :param message: сообщение
    """

    try:
        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Произошла отмена операции")
            return
        else:
            raise AttributeError
    except AttributeError:
        place[4] = message.text
        msg = bot.reply_to(message, "Введи описание места")
        bot.register_next_step_handler(msg, process_description_step, context)


def process_location_step(message, context):
    """
    Получаем от админа координаты места

    :param context: аргументы call-back функции
    :param message: сообщение
    """

    try:
        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Произошла отмена операции")
            return
        else:
            raise AttributeError
    except AttributeError:

        try:
            text = "Введи описание места"
            place[1] = message.venue.location.latitude
            place[2] = message.venue.location.longitude
            place[4] = message.venue.address
            place[0] = message.venue.title
            msg = bot.reply_to(message, text)

            bot.register_next_step_handler(msg, process_description_step, context)
        except AttributeError:
            try:
                place[1] = message.location.latitude
                place[2] = message.location.longitude

                msg = bot.reply_to(message, "Введи название места")
                bot.register_next_step_handler(msg, process_name_step, context)
            except AttributeError:
                msg = bot.reply_to(message, "Отправь геопозицию места только уже правильно")
                try:
                    if message.text.lower() == "нет":
                        bot.send_message(message.chat.id, "Произошла отмена операции")
                        return
                except AttributeError:
                    pass
                bot.register_next_step_handler(msg, process_location_step, context)


def work_with_db_step(message, context):
    """
    Работаем с местом в базе данных через интерфейс админа

    :param context: аргументы call-back функции
    :param message: сообщение
    """

    name = place[0]
    lat = place[1]
    lng = place[2]
    description = place[3]
    address = place[4]

    to_edit = context[0]

    if not to_edit:
        try:
            if message.text.lower() == "да":
                db.insert_place_to_db(name, lat, lng, description, address)
                bot.send_message(message.chat.id, "Место было успешно добавлено")
            elif message.text.lower() == "нет":
                bot.send_message(message.chat.id, "Нет, так нет")
                return
            else:
                raise AttributeError
        except AttributeError:
            msg = bot.reply_to(message, "Глупый что ли? Ответь: да или нет")
            bot.register_next_step_handler(msg, work_with_db_step, context)
    else:
        try:
            if message.text.lower() == "да":
                db.edit_place_from_db(name, lat, lng, description, address, context[1])
                bot.send_message(message.chat.id, "Место было успешно изменено")
            elif message.text.lower() == "нет":
                bot.send_message(message.chat.id, "Нет, так нет")
                return
            else:
                raise AttributeError
        except AttributeError:
            msg = bot.reply_to(message, "Глупый что ли? Ответь: да или нет")
            bot.register_next_step_handler(msg, work_with_db_step, context)


def delete_place_step(message, context):
    """
    Подтверждает удаление места из базы данных

    :param message: сообщение
    :param context: context[0] -- идентификатор места
    :return:
    """
    try:
        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Удаление отменено")
            return
        elif message.text.lower() == "да":
            db.delete_place_from_db(context[0])
            bot.send_message(message.chat.id, text = "Место было успешно удалено")
        else:
            raise AttributeError
    except AttributeError:
        msg = bot.reply_to(message, text = "Так да или нет?")
        bot.register_next_step_handler(msg, delete_place_step, context)


@bot.message_handler(commands = ["send"])
def send_message_to_all(message):
    """
        Обрабатываем команду на отправку сообщения всем пользователям, которая доступна только админам

        :param message: сообщение
        """

    if message.from_user.username in admins:
        msg = bot.reply_to(message, "Привет, " + message.from_user.username +
                           "! Напиши сообщение, которое хочешь отправить!")

        bot.register_next_step_handler(msg, send_msg)
    else:
        return


def send_msg(message):
    if message.text.lower() == "нет":
        bot.send_message(message.chat.id, "Произошла отмена операции")
        return
    send_message.send_message_to_users(message.text)


@bot.message_handler(commands = ["add"])
def add_place(message):
    """
    Обрабатываем команду на добавление места, которая доступна только админам

    :param message: сообщение
    """

    if message.from_user.username in admins:
        to_edit = False
        context = [to_edit]
        msg = bot.reply_to(message, "Привет, " + message.from_user.username +
                           "! Отправь геопозицию места, которое хочешь добавить")

        bot.register_next_step_handler(msg, process_location_step, context)
    else:
        return


@bot.message_handler(commands = ["start"])
def send_location(message):
    """
    Стартовое сообщение для работы бота

    :param message: сообщение
    """

    # Создаем клавиатуру с кнопкой отправки геопозиции
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.resize_keyboard = True
    send_location_btn = types.KeyboardButton("📍 Отправить свое местоположение", request_location = True)
    keyboard.add(send_location_btn)

    # Модифицируем клавиатуру, если пользователь -- админ
    if message.from_user.username in admins:
        add_location_btn = types.KeyboardButton("/add Добавить местоположение")
        send_message_btn = types.KeyboardButton("/send Отправить сообщение")
        keyboard.add(add_location_btn, send_message_btn)
        bot.send_message(message.chat.id, "Здравствуй, сталкер", reply_markup = keyboard)
    else:
        bot.send_message(message.chat.id, "Отправь мне свою геопозицию", reply_markup = keyboard)


@bot.message_handler(content_types = ['location'])
def handle_loc(message):
    """
    Обрабатываем геопозицию, отправленную пользователем

    :param message: сообщение
    """

    db.insert_user_to_db(message)

    usr_lat = message.location.latitude
    usr_lng = message.location.longitude

    # Создаем список, который будет сортировать
    list_of_places: list = []

    # Флаг, указывающий на то, нашел ли бот место в радиусе
    place_found: bool = False

    # Проходим по таблице и вытягиваем данные о месте
    for row in db.get_place_from_db():
        plc_name: str = row[0]
        plc_lat: float = row[1]
        plc_lng: float = row[2]
        plc_desc: str = row[3]
        plc_addr: str = row[4]
        plc_img_url: str = row[5]
        plc_id = str(row[6])

        # Считаем расстояние от пользователя до места из таблицы
        usr_to_plc = count_distance(usr_lat, usr_lng, plc_lat, plc_lng)

        # Создаем странный список-кортеж (??) с дополнительным элементом 'usr_to_plc' (расстояние до объекта)
        # сортируем список по этому значению
        plc: tuple = (plc_name, plc_lat, plc_lng, plc_desc, plc_addr, usr_to_plc, plc_img_url, plc_id)
        list_of_places.append(plc)
        list_of_places = sorted(list_of_places, key = lambda x: x[5])

    # Оставляем 4 ближайших места
    list_of_places = list_of_places[:4]

    for plc in list_of_places:
        # Область, в радиусе (в километрах) которой будем искать заведения
        radius = 5

        # Достаем информацию о месте из кортежа
        name = str(plc[0])
        description = plc[3]
        address = plc[4]
        distance = plc[5]
        img = plc[6]
        id = plc[7]

        # Если нашли место в радиусе
        if distance <= radius:
            place_found = True

            latitude = str(plc[1])
            longitude = str(plc[2])

            # Создаем inline-кнопки для каждого подходящего под условие результата
            inline_keyboard = types.InlineKeyboardMarkup()
            geo_btn = types.InlineKeyboardButton(text = "🗺 Где это?",  # Передаем кнопке тип операции и координаты
                                                 callback_data = "send_location " + latitude + " " + longitude)
            inline_keyboard.add(geo_btn)

            # Добавляем inline-кнопку удаления места для каждого результата, если пользователь -- админ
            if message.from_user.username in admins:
                delete_btn = types.InlineKeyboardButton(text = "❌ Удалить место",
                                                        callback_data = "delete_location " + id)

                edit_btn = types.InlineKeyboardButton(text = "✏️ Изменить место",
                                                      callback_data = "edit_location " + id)
                inline_keyboard.add(edit_btn)
                inline_keyboard.add(delete_btn)

            try:
                if img == 'no_image':
                    raise FileNotFoundError
                # Отправляем сообщение с информацией о месте, фотографией и кнопкой с геопозицией внутри
                im = Image.open(requests.get(img, stream=True).raw, mode = 'r')
                bot.send_photo(message.chat.id, photo = im,
                               caption = send_info(name, description, address, distance),
                               reply_markup = inline_keyboard)
                # Отправляем сообщение с информацией о месте и кнопкой с геопозицией внутри, если фотография не найдена
            except FileNotFoundError or UnboundLocalError or TypeError or MissingSchema:
                bot.send_message(message.chat.id,
                                 text = send_info(name, description, address, distance), reply_markup = inline_keyboard)

    # Если мест в радиусе нет, то уведомляем об этом пользователя
    if not place_found:
        bot.send_message(message.chat.id, "Рядом с вами нет подходящих мест 😞 ")


@bot.callback_query_handler(func = lambda c: True)
def ans(c):
    """
    Обрабатываем нажатия inline-кнопок
    """

    cid = c.message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    if "send_location" in c.data:
        # Парсим координаты из полученных данных после нажатия кнопки и отправляем локацию
        lat = c.data.split(" ")[1]
        lng = c.data.split(" ")[2]
        bot.send_location(cid, lat, lng, reply_markup = keyboard)
    elif "delete_location" in c.data:
        # Парсим идентификатор места, чтобы найти его в БД и удалить
        id = c.data.split(" ")[1]
        context = [id]

        if not db.place_found_in_db(id):
            bot.send_message(cid, "Невозможно удалить. Места нет в базе данных")
        else:
            text = "Точно удалить место?"
            msg = bot.reply_to(c.message, text)
            bot.register_next_step_handler(msg, delete_place_step, context)

    elif "edit_location" in c.data:
        # Парсим идентификатор места, чтобы найти его в БД и изменить
        id = c.data.split(" ")[1]
        to_edit = True
        context = [to_edit, id]

        if not db.place_found_in_db(id):
            bot.send_message(cid, "Невозможно изменить. Места нет в базе данных")
        else:
            msg = bot.reply_to(c.message, "Введи новое название места.")
            try:
                if c.message.text.lower() == "нет":
                    bot.send_message(cid, "Произошла отмена операции")
                    return
            except AttributeError:
                pass

            bot.register_next_step_handler(msg, process_name_step, context)
    else:
        pass


def count_distance(usr_lat, usr_lng, plc_lat, plc_lng):
    """
    Вычисляем расстояние в километрах между двумя точками, учитывая окружность Земли.

    :param usr_lat: координата широты пользователя
    :param usr_lng: координата долготы пользователя
    :param plc_lat: координата широты места
    :param plc_lng: координата долготы места
    :return: расстояние от пользователя до места
    """
    dlng = (plc_lng - usr_lng) * math.pi / 180
    dlat = (plc_lat - usr_lat) * math.pi / 180

    usr_lat = usr_lat * math.pi / 180
    plc_lat = plc_lat * math.pi / 180

    a = pow(sin(dlat / 2), 2) + pow(sin(dlng / 2), 2) * cos(usr_lat) * cos(plc_lat)
    rad = 6371
    c = 2 * asin(sqrt(a))

    km = rad * c

    return round(km, 2)


def main():
    bot.polling(non_stop = True)


if __name__ == '__main__':
    main()
