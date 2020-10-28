import asyncio
import requests
import re
from functools import reduce
from operator import iconcat


async def parse_reesr(url, s):
    data = []
    resp_json = s.get(url).json()
    if resp_json['found'] != 0:
        for j in resp_json['pageData']:
            j['url'] = \
                f'https://www.reestr-zalogov.ru/search/notification/' \
                f'{j["guid"]}'
            data.append(j)
    return data


async def parse_fin(url, s):
    data = []
    resp_json = s.get(url).json()
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


async def get_info(id):
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
        s.cookies = r.history[0].cookies

        urls = [
            f"https://fedresurs.ru/backend/fnp-search/vehicle?&Vin="
            f"{id}&Offset=0&Limit=20",
            f"https://fedresurs.ru/backend/fnp-search/vehicle?&Pin="
            f"{id}&Offset=0&Limit=20",
            f"https://fedresurs.ru/backend/fnp-search/vehicle?&BodyNum="
            f"{id}&Offset=0&Limit=20",
            f"https://fedresurs.ru/backend/fnp-search/vehicle?&Chassis="
            f"{id}&Offset=0&Limit=20",
            f"https://fedresurs.ru/backend/fnp-search/id?&"
            f"Id={id}&Offset=0&Limit=20",
            f"https://fedresurs.ru/backend/encumbrances?startIndex=0&pageSize=15&additionalSearchFnp=true&searchString={id}&group=null&publishDateStart=null&publishDateEnd=null",
        ]
        s.headers["referer"] = \
            f"https://fedresurs.ru/search/encumbrances?searchString" \
            f"={id}&group=All&additionalSearchFnp=true"

        coros = []
        for url in urls[:-1]:
            coros.append(parse_reesr(url, s))
        coros.append(parse_fin(urls[-1], s))
        data = await asyncio.gather(*coros)
        return reduce(iconcat, data, [])


if __name__ == "__main__":
    vin = "7JRZS08ACLG032739"

    loop = asyncio.get_event_loop()
    loop = loop.run_until_complete(get_info(vin))
    loop.close()

    data = get_info(vin)
    print(data)
