import requests

import config
from DBManager import DataBaseManager
from config import *

db = DataBaseManager(db_host, db_name, db_user, db_pass)


def send_message_to_users(message: str):
    for i in db.get_users_from_db():
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id={i[3]}&text={message}"
        requests.post(url)


def main():
    msg: str = str(input("Введите сообщение для пользователя"))
    answer: str = input("Вы уверены, что хотите отправить сообщения? y/n")

    if answer.lower() == "y":
        send_message_to_users(msg)
    elif answer.lower() == "n":
        print("Отмена операции")
        return
    else:
        print("Ошибка ввода")
        return


if __name__ == '__main__':
    main()
