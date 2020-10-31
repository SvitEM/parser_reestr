import re
import asyncio
import aiohttp
from aiohttp import web
from urllib import parse
from functools import reduce
from operator import iconcat

from utils import validate_reestr, reestr_bday_validator


async def parse_reestr(
        url: dict,
        search_type: str,
        session: aiohttp.ClientSession
) -> list:
    data = []
    bday = []
    if 'bday' in url:
        bday = url.pop('bday').split('-')
    rsp = f'https://fedresurs.ru/backend/fnp-search/{search_type}'

    resp = await session.get(url=rsp, params=url)
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
    print(resp_json)
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


async def get_info(request: web.Request) -> list:
    params = validate_reestr(request)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "ru",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        resp = await session.get("https://fedresurs.ru/")
        await resp.text()
        urls = validate_reestr(request)
        session.headers["referer"] = f"https://fedresurs.ru/search/encumbrances?searchString={parse.quote(request.rel_url.query['id'])}&group=All&additionalSearchFnp=true"

        coros = []
        for url in urls:
            coros.append(
                parse_reestr(
                    url=url,
                    search_type=request.rel_url.query['type'],
                    session=session
                )
            )

        # coros.append(parse_fin(urls[-1], s))

        data = await asyncio.gather(*coros)
        return reduce(iconcat, data, [])
