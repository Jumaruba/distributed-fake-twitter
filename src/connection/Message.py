import json
from datetime import datetime
from time import time, strftime, localtime
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
            "post_id": post_id,
            "sender": username,
            "body": body,
        })

    # -------------------------------------------------------------------------
    # Creation and parsing
    # -------------------------------------------------------------------------

    @staticmethod
    def new(operation, args):
        args["operation"] = operation
        args["timestamp"] = str(Message.get_time())
        return json.dumps(args) 

    @staticmethod
    def parse_json(line):
        line = line.strip()
        line = line.decode()
        return json.loads(line)

    @staticmethod
    def get_time():
        ntpclient = ntplib.NTPClient()
        response = ntpclient.request('europe.pool.ntp.org', version=3)
        return strftime('%Y-%m-%d %H:%M:%S', localtime(response.tx_time))

    @staticmethod
    def get_operation(message):
        return message["operation"]
