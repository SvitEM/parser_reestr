import html
import json
import re
import urllib
from urllib import parse
import config


def validate_reestr(request) -> list:
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
            # d['LastName'] = urllib.parse.quote(last_name)
            d['LastName'] = last_name
            # d['FirstName'] = urllib.parse.quote(first_name)
            d['FirstName'] = first_name
            # d['MiddleName'] = urllib.parse.quote(middle_name)
            d['MiddleName'] = middle_name
            d['bday'] = request.rel_url.query['bday']
        else:
            for param in req:
                print(param)
                d[param] = id
        d.update(config.reestr_params)
        urls.append(d)

    return urls


# def generate_get_url(url: str, params: dict) -> str:
#     url += '?'
#     ferst = True
#     for param in params:
#         url += f'{"&" if not ferst else "" }{param}={params[param]}'
#         ferst = False
#     return url

def reestr_bday_validator(requests, j, url, bday) -> bool:
    in_data = False
    resp = requests.get(j['url'])
    content = str(resp.content)
    content = re.findall('notification=.*}"', content)[0][14:-1]
    content = html.unescape(content)
    content = json.loads(content)
    person_name = f"{url['FirstName'].upper()} {url['MiddleName'].upper()} {url['LastName'].upper()}"
    person_birthday = f'{bday[2]}-{bday[1]}-{bday[0]}'
    for pledgors in content['pledgors']:
        if 'privatePerson' in pledgors:
            if pledgors['privatePerson']['name'] == person_name and \
                    pledgors['privatePerson']['birthday'] == person_birthday:
                in_data = True
    for pledgees in content['pledgees']:
        if 'privatePerson' in pledgees:
            if pledgees['privatePerson']['name'] == person_name and \
                    pledgees['privatePerson']['birthday'] == person_birthday:
                in_data = True
    return in_data