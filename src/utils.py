import asyncio
from time import strftime, localtime
import ntplib
from .consts import NTP_MAX_TRIES


def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)


# TODO: understand why NTP keeps failing all the time
def get_time():
    ntpclient = ntplib.NTPClient()

    for _ in range(NTP_MAX_TRIES):
        try:
            response = ntpclient.request('pool.ntp.org')
            return strftime('%Y-%m-%d %H:%M:%S', localtime(response.tx_time))
        except ntplib.NTPException:
            print("NTP try failed")
            pass
    raise ntplib.NTPException 


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
