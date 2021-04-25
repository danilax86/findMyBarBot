import requests

import config
from DBManager import DataBaseManager
from config import *

db = DataBaseManager(db_host, db_name, db_user, db_pass)


def send_message_to_users(message: str):
    for i in db.get_users_from_db():
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id={i[3]}&text={message}"
        requests.post(url)