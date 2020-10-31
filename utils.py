import aiohttp
from aiohttp import web
import html
import json
import re

import config


def validate_reestr(request: web.Request) -> list:
    id = request.rel_url.query['id']
    search_type = request.rel_url.query['type']
    if search_type not in config.allowed_types:
        raise ValueError(
            f'Wrong search type, allowed types: {config.allowed_types}'
        )

    urls = []
    for req in config.reestr[search_type]:
        d = {}
        if search_type == 'person':
            last_name, first_name, middle_name = id.split(' ')
            d['LastName'] = last_name
            d['FirstName'] = first_name
            d['MiddleName'] = middle_name
            d['bday'] = request.rel_url.query['bday']
        else:
            for param in req:
                print(param)
                d[param] = id
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
        for pledgors in content['pledgors']:
            if 'privatePerson' in pledgors:
                if pledgors['privatePerson']['name'].upper() == person_name and \
                        pledgors['privatePerson']['birthday'] == person_birthday:
                    in_data = True
        for pledgees in content['pledgees']:
            if 'privatePerson' in pledgees:
                if pledgees['privatePerson']['name'].upper() == person_name and \
                        pledgees['privatePerson']['birthday'] == person_birthday:
                    in_data = True
    return in_data
