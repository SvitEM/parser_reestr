allowed_types = ['company', 'vehicle', 'person']

reestr = {
    'id': [['Id']],
    'company': [['Name']],
    'nonresidentcompany': [['Name'], ['AnalogInn'], ['RegNum']],
    'vehicle': [['Pin'], ['Vin'], ['BodyNum'], ['Chassis']],
    'person': [['LastName', 'FirstName', 'MiddleName', 'Bday']]
}

reestr_params = {
    'Offset': 0,
    'Limit': 20,
}

encumbrances_params = {
    'startIndex': '0',
    'pageSize': '1000000000',
    'additionalSearchFnp': 'true',
    'group': 'null',
    'publishDateStart': 'null',
    'publishDateEnd': 'null',
    'attempt': '1',
}

encumbrances = {
    'searchString': ""
}

output_dist = 'output/'
