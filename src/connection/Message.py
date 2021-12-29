import json
from datetime import datetime


class Message:
    @staticmethod
    def follow(username):
        return json.dumps({
            "operation": "follow",
            "username": username,
            "timestamp": str(datetime.now())
        });
