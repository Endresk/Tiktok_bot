import sqlite3
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", )


class Database:
    """ Класс работы с базой данных """

    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f"database/{self.name}.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        bool_value = cursor.fetchone()

        if not bool_value:
            cursor.execute('''CREATE TABLE users (
                                           user_id INTEGER NOT NULL,
                                           chat_id INTEGER DEFAULT 0,
                                           chat_member VARCHAR DEFAULT member
                               );
                            ''')
            cursor.execute('''CREATE TABLE chats (
                                           chat_id INTEGER NOT NULL,
                                           choice INTEGER DEFAULT 0
                               );
                            ''')
            logging.info("Database created")
        connection.commit()
        cursor.close()

    def connection(self):
        db_path = os.path.join(os.getcwd(), f"database/{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"database/{self.name}.db")

    def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchall()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def insert_users(self, user_id: int):
        insert_query = f"""INSERT INTO users (user_id)
                           VALUES ({user_id})"""
        self._execute_query(insert_query)
        logging.info(f"Mode for user {user_id} added")

    async def insert_users_anonymous(self, user_id: int,  chat_id: int, chat_member: str):
        insert_query_anonymous = f"""INSERT INTO users (user_id, chat_id, chat_member)
                           VALUES ('{user_id}', '{chat_id}', '{chat_member}')"""
        self._execute_query(insert_query_anonymous)
        logging.info(f"Anonymous user {user_id},  {chat_id}, {chat_member} added")

    async def select_users_anonymous(self, user_id: int, chat_id: int):
        select_query_anonymous = f"""SELECT user_id, chat_id from users 
                           where user_id = {user_id} and chat_id = {chat_id}"""
        record = self._execute_query(select_query_anonymous, select=True)
        return record

    async def select_users(self, user_id: int):
        select_query = f"""SELECT * from users 
                           where user_id = {user_id}"""
        record = self._execute_query(select_query, select=True)
        return record

    async def select_users_chat(self, chat_id: int):
        select_users_chat = f"""SELECT * from users 
                           where chat_id = {chat_id}"""
        record = self._execute_query(select_users_chat, select=True)
        return record

    async def update_users_chat(self, user_id: int, chat_id: int, chat_member: str):
        update_users_chat = f"""Update users 
                              set  chat_id = '{chat_id}', 
                              chat_member = '{chat_member}'
                              where user_id = {user_id}"""
        self._execute_query(update_users_chat)
        logging.info(f"User {user_id} updated")

    async def update_users_chat_add(self, user_id: int, chat_id: int, chat_member: str):
        update_users_chat_add = f"""Update users 
                              set chat_id = '{chat_id}',
                              chat_member = '{chat_member}'
                              where user_id = {user_id}"""
        self._execute_query(update_users_chat_add)
        logging.info(f"User {user_id} updated")

    async def update_yes(self, user_id: int, chat_id: int, chat_member: str,
                         temp_chat_id: int, temp_chat_member: str):
        update_query = f"""Update users 
                                 set chat_id = '{chat_id}', 
                                     chat_member = '{chat_member}',
                                     temp_chat_id = '{temp_chat_id}',
                                     temp_chat_member = '{temp_chat_member}'
                                  where user_id = {user_id}"""
        self._execute_query(update_query)
        logging.info(f"User func YES {user_id} updated")

    async def delete_users(self, user_id: int):
        delete_query = f"""DELETE FROM users WHERE user_id = {user_id}"""
        self._execute_query(delete_query)
        logging.info(f"User {user_id} deleted")

    async def insert_chat_id(self, chat_id: int):
        insert_chat_id = f"""INSERT INTO chats (chat_id)
                           VALUES ({chat_id})"""
        self._execute_query(insert_chat_id)
        logging.info(f"Chat {chat_id} added")

    async def select_chats(self, chat_id: int):
        select_chat_id = f"""SELECT * from chats 
                             where chat_id = {chat_id}"""
        record = self._execute_query(select_chat_id, select=True)
        return record

    async def select_chats_all(self):
        select_chats_all = f"""SELECT * from chats"""
        record = self._execute_query(select_chats_all, select=True)
        return record

    async def update_chat_choice(self, chat_id: int, choice: int):
        update_query = f"""Update chats 
                                 set choice = "{choice}" where chat_id = {chat_id}"""
        self._execute_query(update_query)
        logging.info(f"Chat {chat_id} value choice updated")

    async def delete_chats(self, chat_id: int):
        delete_query = f"""DELETE FROM chats WHERE chat_id = {chat_id}"""
        self._execute_query(delete_query)
        logging.info(f"Chat {chat_id} deleted")

    async def delete_user_anonymous(self, user_id: int, chat_id: int):
        delete_query = f"""DELETE FROM users WHERE user_id = {user_id} and chat_id = {chat_id}"""
        self._execute_query(delete_query)
        logging.info(f"User {user_id} deleted")


db = Database('users')
db.create_db()
