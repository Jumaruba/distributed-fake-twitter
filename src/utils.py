import asyncio
from time import time, strftime, localtime
import ntplib


NTPCLIENT = ntplib.NTPClient()


def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)


def get_time():
    ntpclient = ntplib.NTPClient()
    response = ntpclient.request('pool.ntp.org', version=3)
    return strftime('%Y-%m-%d %H:%M:%S', localtime(response.tx_time))
