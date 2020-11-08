import re
import asyncio
import pandas as pd
import aiohttp
from urllib import parse
from functools import reduce
from operator import iconcat

import utils
from utils import validate_reestr, reestr_bday_validator


async def parse_reestr(
        url: dict,
        search_type: str,
        session: aiohttp.ClientSession,
        proxy: str
) -> list:
    data = []
    bday = []
    if 'bday' in url.keys():
        # print(url)
        bday = url.pop('bday').split('-')
    rsp = f'https://fedresurs.ru/backend/fnp-search/{search_type}'
    # print(rsp, url)
    resp = await session.get(url=rsp, params=url, proxy=proxy)
    resp_json = await resp.json()
    if resp_json['found'] != 0:
        for page_data in resp_json['pageData']:
            page_data['url'] = \
                f'https://www.reestr-zalogov.ru/search/notification/' \
                f'{page_data["guid"]}'
            if bday:
                if await reestr_bday_validator(page_data, url, bday):
                    data.append(page_data)
                    continue
                else:
                    continue
            data.append(page_data)
    return data


async def parse_fin(url, s):
    data = []
    resp_json = s.get(url).json()
    # print(resp_json)
    if resp_json['found'] != 0:
        for j in resp_json['pageData']:
            guid = j["guid"]
            main_info = j['mainInfo'].split('\n')
            main_info = [info[:-1] for info in main_info[:-1]]
            pledgors = main_info[-2]
            pledgees = main_info[-1]
            reference_number = j['number']
            registration_time = j['publishDate']
            subjects = re.findall(
                '<res>.*</res>',
                j['bodyHighlights'][0]
            )[0][5:-6]
            data.append({
                'url': f'https://fedresurs.ru/sfactmessage/{guid}',
                'guid': guid,
                'pledgees': [pledgees],
                'pledgors': [pledgors],
                'referenceNumber': reference_number,
                'registrationTime': registration_time,
                'subjects': [subjects],
            })
    return data


async def get_info(
        params: dict,
        session: aiohttp.ClientSession,
        proxy: str
) -> dict:

    urls = validate_reestr(params)
    session.headers[
        "referer"] = f"https://fedresurs.ru/search/encumbrances?searchString={parse.quote(params['id'])}&group=All&additionalSearchFnp=true"
    coros = []
    print(proxy[-5:], params, session.cookie_jar.filter_cookies('https://fedresurs.ru'))
    for url in urls:
        coros.append(
            parse_reestr(
                url=url,
                search_type=params['search_type'],
                session=session,
                proxy=proxy
            )
        )

    # coros.append(parse_fin(urls[-1], s))

    data = await asyncio.gather(*coros)
    data = reduce(iconcat, data, [])
    if params['bday'] is not None:
        data = {
            'id': params['id'],
            'data': data,
            'bday': params['bday'],
        }
    else:
        data = {
            'id': params['id'],
            'data': data,
        }
    return data


async def worker(
        queue: asyncio.Queue,
        queue_get: asyncio.Queue,
        session: aiohttp.ClientSession,
        proxy: str,
        ):
    print(f'start worker with proxy {proxy}')
    while True:
        data = await queue.get()
        info = await get_info(params=data['params'], session=session, proxy=proxy)
        queue_get.put_nowait(info)
        queue.task_done()
        await asyncio.sleep(6)
        # return info


async def get_multy_info(params: dict, proxies: list) -> list:
    queue = asyncio.Queue()
    queue_get = asyncio.Queue()
    data = []
    sessions = []
    for i, ids in enumerate(params['ids'], start=0):
        if 'bday' not in ids.keys():
            bday = None
        else:
            bday = ids['bday']
        search_params = {
            'id': ids['id'],
            'search_type': params['type'],
            'bday': bday,
        }
        queue.put_nowait({
            'params': search_params,
        })
        # print(session.cookie_jar.filter_cookies('https://fedresurs.ru/'))
        # resp_data = await get_info(params=params, session=session)
        # data.append({
        #     'ids': ids,
        #     'data': resp_data,
        # })

    tasks = []
    for proxy in proxies:
        session = await utils.get_session(proxy)
        sessions.append(session)
        task = asyncio.create_task(worker(queue, queue_get, session, proxy))
        tasks.append(task)

    await queue.join()

    for task in tasks:
        task.cancel()
    data = await asyncio.gather(*tasks, return_exceptions=True)
    resp_data = []
    while True:
        d = await queue_get.get()
        resp_data.append(d)
        if queue_get.empty():
            break
    await queue.join()
    for session in sessions:
        await session.close()
    return resp_data


async def get_paused_info(params: dict, proxies=None) -> list:
    if proxies is None:
        proxies = ['']
    to_send = []
    ret = []
    for i, ids in enumerate(params['ids'], start=1):
        to_send.append(ids)
    data = {
        'ids': to_send,
        'type': params['type']
    }
    ret = await get_multy_info(data, proxies)
    df_resp = pd.DataFrame.from_dict(ret)
    df_resp.to_csv('output.csv')
    return ret
