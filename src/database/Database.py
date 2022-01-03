import sqlite3
import json 
from ..consts import DATABASE_FILE_PATH
from os.path import exists

class Database:
    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------

    def __init__(self, username):
        self.database_file_path = f"{DATABASE_FILE_PATH}/{username}.db"  
        exists_db = exists(self.database_file_path)
 
        self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        if not exists_db: 
            self.create_table()

    # -------------------------------------------------------------------------
    # SQL interaction
    # -------------------------------------------------------------------------

    def commit(self, command, arguments=None):
        if arguments is None:
            self.cursor.execute(command)
        else:
            self.cursor.execute(command, arguments)
        self.connection.commit()


    def fetch(self, command, arguments=None):
        if arguments is None:
            self.cursor.execute(command)
        else:
            self.cursor.execute(command, arguments)
        return self.cursor.fetchall()


    def create_table(self):
        self.commit("""CREATE TABLE posts (
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
        self.commit("""INSERT INTO posts(post_id, user, timestamp, body) 
                        VALUES(?,?,?,?)""", [post_id, sender, date, body])


    def get_posts(self):
        return self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            ORDER BY timestamp
        """)


    def get_own_posts(self, username):
        posts = self.fetch("""
            SELECT post_id, user, timestamp, body
            FROM posts
            WHERE user = ?
            ORDER BY timestamp
        """, [username]) 
        positions = ["post_id", "user", "timestamp", "body"] 
        return [dict(zip(positions, value)) for value in posts]
