import aiohttp
from aiohttp import web
import html
import json
import re

import config


def validate_reestr(
        params
) -> list:
    if params['search_type'] not in config.allowed_types:
        raise ValueError(
            f'Wrong search type, allowed types: {config.allowed_types}'
        )

    urls = []
    for req in config.reestr[params['search_type']]:
        d = {}
        if params['search_type'] == 'person':
            last_name, first_name, middle_name = params['id'].split(' ')
            d['LastName'] = last_name
            d['FirstName'] = first_name
            d['MiddleName'] = middle_name
            d['bday'] = params['bday']
        else:
            for param in req:
                # print(param)
                d[param] = params['id']
        d.update(config.reestr_params)
        urls.append(d)

    return urls


async def reestr_bday_validator(page_data: dict, url: dict, bday: list) -> bool:
    in_data = False
    async with aiohttp.ClientSession() as session:
        resp = await session.get(page_data['url'])
        content = str(await resp.content.read())
        content = re.findall("notification=.*}\"", content)[0][14:-1]
        content = html.unescape(content)
        content = json.loads(content)
        person_name = f"{url['FirstName'].upper()} {url['MiddleName'].upper()} {url['LastName'].upper()}"
        person_birthday = f'{bday[2]}-{bday[1]}-{bday[0]}'
        if 'pledgors' in content.keys():
            for pledgors in content['pledgors']:
                if 'privatePerson' in pledgors:
                    if pledgors['privatePerson']['name'].upper() == person_name and \
                            pledgors['privatePerson']['birthday'] == person_birthday:
                        in_data = True
        if 'pledgees' in content.keys():
            for pledgees in content['pledgees']:
                if 'privatePerson' in pledgees:
                    if pledgees['privatePerson']['name'].upper() == person_name and \
                            pledgees['privatePerson']['birthday'] == person_birthday:
                        in_data = True
    return in_data


async def get_session(num='111') -> aiohttp.ClientSession:
    print('create new client session')
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
        "user-agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.{num} Safari/537.36",
    }
    session = aiohttp.ClientSession(headers=headers)
    resp = await session.get("https://fedresurs.ru/")
    return session
