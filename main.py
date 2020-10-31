import asyncio
from aiohttp import web
import uvloop
from concurrent.futures.thread import ThreadPoolExecutor

from parser import get_info


async def parse(request: web.Request) -> web.Response:
    data = await get_info(request)
    print(data)
    return web.json_response(data=data)


async def hello(request: web.Request) -> web.Response:
    return web.json_response(data={'hello from parser': True})


def setup_asyncio():
    uvloop.install()
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(thread_name_prefix="invest_api")
    loop.set_default_executor(executor)


async def main(config=None):
    setup_asyncio()
    app = web.Application()
    app.router.add_get('/', hello)
    app.router.add_get('/parse', parse)
    return app
