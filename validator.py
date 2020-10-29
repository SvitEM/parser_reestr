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
        for param in req:
            d[param] = id
        d.update(config.reestr_params)
        urls.append(d)

    return urls



def validate2(request):
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

