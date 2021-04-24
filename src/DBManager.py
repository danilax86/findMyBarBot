import pymysql
from config import *


class DataBaseManager:
    def __init__(self):
        self.host = db_host
        self.name = db_name
        self.user = db_user
        self.password = db_pass

    def __init__(self, host: str, name: str, user: str, password: str):
        self.host = host
        self.name = name
        self.user = user
        self.password = password

    def get_connection(self) -> pymysql.connect:
        conn = pymysql.connect(host = self.host,
                               database = self.name,
                               user = self.user,
                               password = self.password)
        conn.autocommit(True)
        return conn

    def insert_user_to_db(self, message):
        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        username: str = message.from_user.username
        first_name: str = message.from_user.first_name
        last_name: str = message.from_user.last_name
        chat_id: str = message.from_user.id
        user = (username, first_name, last_name, chat_id)

        # Проверяет, есть ли пользователь в БД
        find_user_query: str = "select username from users where chat_id='{}'".format(user[3])
        cursor.execute(find_user_query)
        user_found = cursor.fetchall()

        # Добавляем пользователя в БД, если его в ней нет
        if not user_found:
            insert_query: str = "insert into users (username, first_name, last_name, chat_id) values ('{}', '{}', " \
                                "'{}', '{}')".format(
                user[0], user[1], user[2], user[3])
            cursor.execute(insert_query)
        else:
            pass

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

    def place_found_in_db(self, id):
        """
        Проверяет, есть ли место в базе данных

        :param id: идентификатор места
        :return: False, если нет
        """
        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # Проверяет, есть ли место в БД
        find_place_query: str = "select id from places where id='{}'".format(id)
        cursor.execute(find_place_query)
        result = cursor.fetchall()

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

        return result

    def insert_place_to_db(self, name, lat, lng, description, address):
        """
        Добавляем место в базу данных

        :param name: название места
        :param lat: широта
        :param lng: долгота
        :param description: описание
        :param address: адрес
        """

        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # SQL query для добавления места в БД
        insert_query: str = "insert into places (name, lat, lng, description, address) values ('{}', '{}', '{}', " \
                            "'{}', '{}')".format(name, lat, lng, description, address)
        cursor.execute(insert_query)

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

    def delete_place_from_db(self, id):
        """
        Удаляем место из базы данных

        :param id: идентификатор места в БД
        """

        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # SQL query для удаления места из БД
        delete_query: str = "delete from places where id = '{}'".format(id)
        cursor.execute(delete_query)

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

    def edit_place_from_db(self, name, lat, lng, description, address, id):
        """
        Изменяем место в базе данных

        :param id: идентификатор места в БД
        :param description: описание места
        :param lng: долгота
        :param lat: ширина
        :param address: адрес
        :param name: название места
        """

        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # SQL query для удаления места из БД
        edit_query: str = "update places set name='{}', lat='{}', lng='{}', description='{}', address='{}' where " \
                          "id='{}'" \
            .format(name, lat, lng, description, address, id)
        cursor.execute(edit_query)

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

    def get_place_from_db(self):
        """
        Возвращаем таблицу мест из базы данных

        :return: таблица мест
        """

        select_query: str = "select * from places"

        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # Возвращаем таблицу из БД
        cursor.execute(select_query)
        result = cursor.fetchall()

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

        return result

    def get_users_from_db(self):
        """
        Возвращаем таблицу мест из базы данных

        :param db_connection: инициализатор базы данных
        :return: таблица мест
        """

        select_query: str = "select * from users"

        # Создаем курсор и присоединяемся к БД
        cursor = self.get_connection().cursor()

        # Возвращаем таблицу из БД
        cursor.execute(select_query)
        result = cursor.fetchall()

        # Закрываем соединение
        cursor.close()
        self.get_connection().close()

        return result
