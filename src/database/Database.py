import sqlite3
import json 
from datetime import datetime
from ..consts import DATABASE_FILE_PATH

class Database:
    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------

    def __init__(self, username):
        self.database_file_path = f"{DATABASE_FILE_PATH}/{username}.db" 
        self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
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

    def fetch(self, command):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def create_table(self):
        #TODO: if table exists do nothing.
        self.commit("DROP TABLE IF EXISTS messages")
        self.commit("""CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
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
        self.commit("""INSERT INTO messages(message_id, user, timestamp, body) 
                        VALUES(?,?,?,?)""", [post_id, sender, date, body])


    def get_messages(self):
        return self.fetch("""
            SELECT message_id, user, timestamp, body
            FROM messages
            ORDER BY timestamp
        """)
