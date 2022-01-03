import asyncio

def run_in_loop(function, loop):
    return asyncio.run_coroutine_threadsafe(function, loop)