import sqlite3
import time


class Datebase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ? AND chat_id = ?",
                                         (user_id, chat_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, chat_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id,))

    def mute(self, user_id, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM users WHERE user_id = ? AND chat_id = ?",
                                       (user_id, chat_id,)).fetchone()
            return int(user[2]) >= int(time.time())

    def add_mute(self, user_id, chat_id, mute_time):
        with self.connection:
            return self.cursor.execute("UPDATE users SET mute_time = ? WHERE user_id = ? AND chat_id = ?",
                                       (int(time.time()) +
                                        mute_time, user_id, chat_id,))

    def admin_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM admins WHERE admin_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_code(self, user_id, code):
        with self.connection:
            return self.cursor.execute("UPDATE admins SET admin_code = ? WHERE admin_id = ?", (code, user_id,))

    def check_code(self, code):
        with self.connection:
            return len(self.cursor.execute("SELECT * FROM admins WHERE admin_code = ?", (code,)).fetchall())

    def del_code(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE admins SET admin_code = '' WHERE admin_id = ?", (user_id,))

    def get_code(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT admin_code FROM admins WHERE admin_id = ?", (user_id,)).fetchone()

    def add_admin(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO admins (admin_id) VALUES (?)", (user_id,))

    def admin_chat(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT admin_chat FROM admins WHERE admin_id = ?", (user_id,)).fetchall()

    def update_admin_chat(self, chats, admin_id):
        with self.connection:
            return self.cursor.execute("UPDATE admins SET admin_chat = ? WHERE admin_id = ?", (chats, admin_id,))

    def chat_exists(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,)).fetchall()
            return bool(len(result))

    def add_chat(self, chat_id, title):
        with self.connection:
            return self.cursor.execute("INSERT INTO chats (chat_id, title) VALUES (?, ?)", (chat_id, title,))

    def set_defult(self, chat_id, args):
        for i, j in args.items():
            self.cursor.execute(f"UPDATE chats SET {i} = ? WHERE chat_id = ?", (j, chat_id,))

    def get_chat(self, chat_id, date):
        st = ''
        for i in date:
            if st == '':
                st = i
            else:
                st = st + f', {i}'
        return self.cursor.execute(f"SELECT {st} FROM chats WHERE chat_id = ?", (chat_id,)).fetchone()
