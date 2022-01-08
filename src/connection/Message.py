import json
from time import time, strftime, localtime
from ..utils import get_time


class Message:

    # -------------------------------------------------------------------------
    # Operation specific messages
    # -------------------------------------------------------------------------

    @staticmethod
    def sync_posts(sender, last_post_id, username):
        return Message.new(sender, "sync_posts", {
            "last_post_id": last_post_id,
            "username": username,
        })

    @staticmethod
    def follow(sender):
        return Message.new(sender, "follow", {})

    @staticmethod
    def unfollow(sender):
        return Message.new(sender, "unfollow", {})

    @staticmethod
    def post(post_id, sender, body, timestamp=None):
        args = {
            "post_id": post_id,
            "body": body,
        }

        if timestamp is not None:
            args["timestamp"] = timestamp
        return Message.new(sender, "post", args)

    # -------------------------------------------------------------------------
    # Creation and parsing
    # -------------------------------------------------------------------------

    @staticmethod
    def new(sender, operation, args):
        args["sender"] = sender
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
