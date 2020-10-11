import sqlite3 as sql
from task import To_do


class Data:
    def __init__(self):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()

            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                bot_status TEXT DEFAULT waiting,
                username TEXT
                )""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                            user_id INTEGER,
                            task_id INTEGER,
                            title TEXT,
                            text TEXT,
                            out TEXT,
                            active INTEGER DEFAULT 1,
                            deleted INTEGER DEFAULT 0
                            )""")

    def register_user(self, user_id, username):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (user_id, username) VALUES(?, ?)", (user_id, username))

    def is_registered(self, user_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = (?)", tuple([user_id]))
            ans = cursor.fetchone()
            if ans:
                return True
            else:
                return False

    def create_task(self, user_id, task):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task_id FROM tasks WHERE user_id = (?) ORDER BY task_id", tuple([user_id]))
            task_id = 1
            indexes = list(cursor.fetchall())
            for possible_index in indexes:
                if task_id != possible_index[0]:
                    break
                task_id += 1
            cursor.execute("INSERT INTO tasks (user_id, task_id, title, text, out) VALUES(?,?,?,?,?)",
                           (user_id, task_id, task.title, task.text, task.out))

    def update_task(self, user_id, task):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE tasks SET title = (?), text = (?), out = (?), active = (?) WHERE user_id = (?) AND "
                           "task_id = (?)", (task.title, task.text, task.out, task.active, user_id, task.id))

    def get_task(self, user_id, task_id):
        task = To_do()
        task.id = task_id
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM tasks WHERE user_id = (?) AND task_id = (?)", (user_id, task_id))
            temp = cursor.fetchall()
            if not temp:
                return 0
            cursor.execute("SELECT title, text, out, active FROM tasks WHERE user_id = (?) AND task_id = (?)",
                           (user_id, task_id))
            temp = cursor.fetchone()
            task.title = temp[0]
            task.text = temp[1]
            task.out = temp[2]
            if not temp[3]:
                task.active = False
        return task

    def bot_status(self, user_id, status=''):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            if status:
                cursor.execute("UPDATE users SET bot_status = (?) WHERE user_id = (?)", (status, user_id))
            else:
                cursor.execute("SELECT bot_status FROM users WHERE user_id = (?)", tuple([user_id]))
                return cursor.fetchone()[0]

    def delete_task(self, user_id, task_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM tasks WHERE user_id = (?) AND task_id = (?)", (user_id, task_id))

    def tasks_exist(self, user_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM tasks WHERE user_id = (?)", tuple([user_id]))
            if cursor.fetchall():
                return True
            else:
                return False

    def get_index_of_the_last_task(self, user_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT max(task_id) FROM tasks WHERE user_id = (?)", tuple([user_id]))
            return cursor.fetchone()[0]

    def task_done(self, user_id, task_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE tasks SET active = 0 WHERE user_id = (?) AND task_id = (?)", (user_id, task_id))

    def get_user_ids(self):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM users")
            return cursor.fetchall()

    def delete_user(self, user_id):
        with sql.connect("users_data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = (?)", tuple([user_id]))
            cursor.execute("DELETE FROM tasks WHERE user_id = (?)", tuple([user_id]))
