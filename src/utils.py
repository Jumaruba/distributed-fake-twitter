import asyncio
from time import strftime, localtime
import ntplib
from .consts import NTP_SERVER, NTP_FREQ, NTP_TRIES
import os
from datetime import datetime
import threading


def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)


def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_ntp_thread():
    return threading.Timer(NTP_FREQ, sync_time)


def sync_time():
    ntpclient = ntplib.NTPClient()
    for _ in range(NTP_TRIES):
        try:
            response = ntpclient.request(NTP_SERVER)
            ntp_time = strftime('%m%d%H%M%Y.%S', localtime(response.tx_time))
            os.system('date', ntp_time)
            return 
        except ntplib.NTPException:
            # print("NTP try failed")
            pass


def read_ips(file_path):
    with open(file_path) as file:
        lines = file.readlines()

    def parse_line(line):
        line = line.strip()
        line = line.split()
        line[1] = int(line[1])
        return tuple(line)

    return list(map(parse_line, lines))

# -------------------------------------------------------------------------
# Post utils
# -------------------------------------------------------------------------


def get_post_args(post):
    post_id = post["post_id"]
    user = post["user"]
    date = post["timestamp"]
    body = post["body"]
    return [post_id, user, date, body]


def get_post_fieldnames():
    return ["post_id", "user", "timestamp", "body"]


def post_tuple_to_dict(post):
    positions = get_post_fieldnames()
    return dict(zip(positions, post))


def parse_post(post):
    post_id, post_creator, post_time, post_content = post
    post_time = post_time.split()
    post_day = post_time[0]
    post_hour = post_time[1]
    return post_id, post_creator, post_day, post_hour, post_content
