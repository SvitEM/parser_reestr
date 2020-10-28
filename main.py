from concurrent.futures.thread import ThreadPoolExecutor

from aiohttp import web
import asyncio
from parser import get_info
import uvloop


async def parse(request):
    id = request.rel_url.query['id']
    data = await get_info(id)
    # data = {'example': 'example1'}
    return web.json_response(data=data)


async def hello(request):
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


# app = main()
# if __name__ == '__main__':
#     main()

