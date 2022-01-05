import asyncio
from time import time, strftime, localtime
import ntplib
from .consts import NTP_MAX_TRIES


NTPCLIENT = ntplib.NTPClient()


def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)


def get_time():
    ntpclient = ntplib.NTPClient()
    for _ in range(NTP_MAX_TRIES):
        try:
            response = ntpclient.request('pool.ntp.org', version=3)
            break
        except ntplib.NTPException:
            pass
    return strftime('%Y-%m-%d %H:%M:%S', localtime(response.tx_time))
