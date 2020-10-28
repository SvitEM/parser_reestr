from aiohttp import web
import asyncio
from parser import get_info

routes = web.RouteTableDef()


@routes.get('/parse')
async def hello(request):
    id = request.rel_url.query['id']
    data = await get_info(id)
    # data = {'example': 'example1'}
    return web.json_response(data=data)

@routes.get('/')
async def hello(request):
    return web.Response(text='hello to parser')


def main(*args, **kwargs):
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)

if __name__ == '__main__':
    main()

