import asyncio
import html
import json
import urllib
from urllib import parse
from validator import validate_reestr, reestr_bday_validator

import requests
import re
from functools import reduce
from operator import iconcat


async def parse_reestr(url: dict, search_type: str, s):
    data = []
    bday = []
    if 'bday' in url:
        bday = url.pop('bday').split('-')
    rsp = f'https://fedresurs.ru/backend/fnp-search/{search_type}'
    print(url)
    resp = s.get(rsp, params=url)
    resp_json = resp.json()
    print(resp_json)
    if resp_json['found'] != 0:
        for j in resp_json['pageData']:
            j['url'] = \
                f'https://www.reestr-zalogov.ru/search/notification/' \
                f'{j["guid"]}'
            if bday:
                if reestr_bday_validator(requests, j, url, bday):
                    data.append(j)
                    print(url, data)
                    continue
                else:
                    continue
            data.append(j)
            print(url, data)
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


def validate(request):
    params = {}
    params['id'] = request.rel_url.query['id']
    params['id'] = parse.quote(params['id'])
    params['type'] = False
    try:
        if request.rel_url.query['type'] == 'true':
            params['type'] = True
    except KeyError as e:
        pass
    if params['type']:
        params['b_day'], params['b_month'], params['b_year'] = \
            request.rel_url.query['bday'].split('-')
    print(params)
    return params


async def get_info(request):
    params = validate_reestr(request)
    
    r = requests.Response()
    with requests.Session() as s:
        s.headers = {
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
        r = s.get("https://fedresurs.ru/")
        print('get cookies')
        s.cookies = r.history[0].cookies
        print(dict(s.cookies))
        print('validate_reestr')
        urls = validate_reestr(request)
        print(urls)
        s.headers["referer"] = f"https://fedresurs.ru/search/encumbrances?searchString={urllib.parse.quote(request.rel_url.query['id'])}&group=All&additionalSearchFnp=true"
        # print(s.headers['referer'])
        coros = []
        for url in urls:
            coros.append(
                parse_reestr(
                    url=url,
                    search_type=request.rel_url.query['type'],
                    s=s
                )
            )
        # coros.append(parse_fin(urls[-1], s))
        data = await asyncio.gather(*coros)
        return reduce(iconcat, data, [])


if __name__ == "__main__":
    vin = "7JRZS08ACLG032739"

    loop = asyncio.get_event_loop()
    loop = loop.run_until_complete(get_info(vin))
    loop.close()

    data = get_info(vin)
    print(data)