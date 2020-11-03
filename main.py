import asyncio
from aiohttp import web
import uvloop
from concurrent.futures.thread import ThreadPoolExecutor

from parser import get_info, get_multy_info, get_paused_info
import utils


async def parse(request: web.Request) -> web.Response:
    if 'bday' in request.rel_url.query.keys():
        bday = request.rel_url.query['bday']
    else:
        bday = None

    params = {
        'id': request.rel_url.query['id'],
        'search_type': request.rel_url.query['type'],
        'bday': bday
    }
    session = await utils.get_session()
    data = await get_info(params=params, session=session)
    await session.close()
    # print(data)
    return web.json_response(data=data)


async def parse_multy(request: web.Request) -> web.Response:
    # print(await request.json())
    # data = await get_multy_info(params=await request.json())
    data = await get_paused_info(params=await request.json())
    # data = {
    #     'ids': data
    # }
    # print(data)
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
    app.router.add_post('/parse-multy', parse_multy)
    return app
