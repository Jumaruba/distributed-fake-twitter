import sqlite3

from ..consts import DATABASE_FILE_PATH

class Database:
    # -------------------------------------------------------------------------
    # Creation and instance getter
    # -------------------------------------------------------------------------

    def __new__(cls):
        # Singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
            cls.instance.init()
            cls.create_table()
        return cls.instance

    def init(self):
        self.connection = sqlite3.connect(DATABASE_FILE_PATH)
        self.cursor = self.connection.cursor()

    # -------------------------------------------------------------------------
    # SQL interaction
    # -------------------------------------------------------------------------

    @staticmethod
    def commit(command, arguments=None):
        instance = Database()
        cursor = instance.cursor
        if arguments is None:
            cursor.execute(command)
        else:
            cursor.executemany(command, arguments)
        instance.connection.commit()

    @staticmethod
    def fetch(command):
        instance = Database()
        cursor = instance.cursor
        cursor.execute(command)
        return instance.connection.fetchall()

    @staticmethod
    def create_table():
        Database.commit("DROP TABLE IF EXISTS messages")
        # TODO: Fix the types of the attributes
        Database.commit("""CREATE TABLE messages (
            message_id SERIAL PRIMARY KEY,
            user VARCHAR(20) NOT NULL,
            timestamp DATETIME NOT NULL,
            body VARCHAR NOT NULL
        );""")

    # -------------------------------------------------------------------------
    # Specific functions for the context
    # -------------------------------------------------------------------------

    @staticmethod
    def insert(message_id, user, timestamp, body):
        Database.commit("""
            INSERT INTO messages(message_id, user, timestamp, body)
            VALUES(?, ?, ?, ?)
        """, [message_id, user, timestamp, body])

    @staticmethod
    def get_messages():
        return Database.fetch("""
            SELECT message_id, user, timestamp, body
            FROM messages
            ORDER BY timestamp
        """)
