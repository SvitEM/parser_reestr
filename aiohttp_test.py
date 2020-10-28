from aiohttp import web
import asyncio
from test1 import get_info

routes = web.RouteTableDef()


@routes.get('/parse')
async def hello(request):
    id = request.rel_url.query['id']
    data = await get_info(id)
    # data = {'example': 'example1'}
    return web.json_response(data=data)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)

