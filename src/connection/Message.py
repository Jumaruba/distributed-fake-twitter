import json
from time import time, strftime, localtime
from ..utils import get_time


class Message:

    # -------------------------------------------------------------------------
    # Operation specific messages
    # -------------------------------------------------------------------------

    @staticmethod
    def follow(username):
        return Message.new("follow", {
            "username": username,
        })

    @staticmethod
    def post(post_id, username, body, timestamp=None):
        args = {"post_id": post_id,
                "sender": username,
                "body": body,
                }

        if timestamp is not None:
            args["timestamp"] = timestamp
        return Message.new("post", args)

    # -------------------------------------------------------------------------
    # Creation and parsing
    # -------------------------------------------------------------------------

    @staticmethod
    def new(operation, args):
        args["operation"] = operation
        if "timestamp" not in args:
            args["timestamp"] = str(get_time())
        return json.dumps(args)

    @staticmethod
    def parse_json(line):
        line = line.strip()
        line = line.decode()
        return json.loads(line)

    @staticmethod
    def get_operation(message):
        return message["operation"]
