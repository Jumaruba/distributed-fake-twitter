import asyncio
from time import strftime, localtime
import ntplib
from .consts import NTP_MAX_TRIES


NTPCLIENT = ntplib.NTPClient()


def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)


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