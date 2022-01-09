import sqlite3
import json
from ..consts import DATABASE_FILE_PATH, POST_LIFETIME
from os.path import exists


class Database:
    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------

    def __init__(self, username):
        self.database_file_path = f"{DATABASE_FILE_PATH}/{username}.db"
        exists_db = exists(self.database_file_path)

        self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False, isolation_level=None)
        self.cursor = self.connection.cursor()
        if not exists_db:
            self.create_table()

    # -------------------------------------------------------------------------
    # SQL interaction
    # ------------------------------------------------------------------------- 

    def execute(self, command, arguments=None):
        if arguments is None:
            self.cursor.execute(command)
        else:
            self.cursor.execute(command, arguments)

    def fetch(self, command, arguments=None):
        if arguments is None:
            self.cursor.execute(command)
        else:
            self.cursor.execute(command, arguments)
        return self.cursor.fetchall()

    def create_table(self):
        self.execute("""
            CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user VARCHAR(20) NOT NULL,
            timestamp DATETIME NOT NULL,
            body VARCHAR(50) NOT NULL 
        );""")

    # -------------------------------------------------------------------------
    # Specific functions for the context
    # -------------------------------------------------------------------------

    def insert(self, message: str):
        message = json.loads(message)
        post_id = message["post_id"]
        sender = message["sender"]
        date = message["timestamp"]
        body = message["body"]
        self.execute("""
            INSERT INTO posts(post_id, user, timestamp, body) 
            VALUES(?,?,?,?)
        """, [post_id, sender, date, body])


    def add_posts(self, posts):
        posts_list = json.loads(posts)
        for post in posts_list:
            self.execute("""
                INSERT INTO posts(post_id, user, timestamp, body) 
                VALUES(?,?,?,?)
            """, [post["post_id"], post["user"], post["timestamp"], post["body"]])


    def has_post(self, post_id, username):
        post = self.fetch("""
            SELECT post_id 
            FROM posts 
            WHERE post_id=? AND user=?
            """, [post_id, username]) 
        return len(post) != 0 

    
    def update_post(self, post_id, username, new_timestamp, new_post_id):
        self.cursor.execute("""
                UPDATE posts
                SET timestamp = ?, post_id = ? 
                WHERE post_id = ? AND user = ?
            """, [new_timestamp, new_post_id, post_id, username])    


    def delete(self, username, timestamp_now):
        self.execute("""
            DELETE FROM posts 
            WHERE user != ?
            AND timestamp < datetime(?, ?)
        """, [username, timestamp_now, f"-{POST_LIFETIME} seconds"])


    def get_all_posts(self):
        return self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            ORDER BY timestamp
        """)

    def get_old_posts(self, username, timestamp_now): 
        return self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts 
            WHERE user = ?
            AND timestamp < datetime(?, ?)
            ORDER BY timestamp
        """, [username, timestamp_now, f"-{POST_LIFETIME} seconds"])

    # TODO change to last post
    def last_message(self, username):
        return self.fetch("""
            SELECT MAX(post_id)
            FROM posts
            WHERE user == ?
        """, [username])[0][0]

    def get_posts(self, username, timestamp_now):
        posts = self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            WHERE user = ?
            AND timestamp > datetime(?, ?)
            ORDER BY timestamp
        """, [username, timestamp_now, f"-{POST_LIFETIME} seconds"])
        positions = ["post_id", "user", "timestamp", "body"]
        return [dict(zip(positions, value)) for value in posts]

    def get_post(self, post_id):
        post =  self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            WHERE post_id = ?
        """, [post_id])[0]
        positions = ["post_id", "sender", "timestamp", "body"]  
        dictionary = dict(zip(positions, post))
        print(dictionary)
        return dictionary


    def get_posts_after(self, username, last_post_id):
        posts = self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            WHERE user = ?
            AND post_id > ?
            ORDER BY timestamp
        """, [username, last_post_id])
        positions = ["post_id", "user", "timestamp", "body"]
        return [dict(zip(positions, value)) for value in posts]
