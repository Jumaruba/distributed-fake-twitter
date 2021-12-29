import json
from datetime import datetime
import ntplib

NTPCLIENT = ntplib.NTPClient()


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
    def post(post_id, username, body):
        return Message.new("post", {
            "id": post_id,
            "sender": username,
            "body": body,
        })

    # -------------------------------------------------------------------------
    # Creation and parsing
    # -------------------------------------------------------------------------

    @staticmethod
    def new(operation, args):
        args["operation"] = operation
        args["timestamp"] = str(datetime.now())
        return json.dumps(args)

    @staticmethod
    def parse_json(line):
        line = line.strip()
        line = line.decode()
        return json.loads(line)

    @staticmethod
    def get_time():
        time = ntplib.NTPClient()
        try:
            response = time.request('europe.pool.ntp.org', version=3)
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def get_operation(message):
        return message["operation"]
