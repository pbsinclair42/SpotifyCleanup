import json
import untangle
from requests import request, Request


def httpRequest(url, params, headers, method='get', responseFormat='json', data=None):
    formatMapping = {'json': json.loads, 'xml': untangle.parse, None: None}

    if responseFormat not in formatMapping.keys():
        raise ValueError("Unknown format " + responseFormat)

    if data != None:
        data = json.dumps(data)

    response = request(method, url=url, headers=headers, params=params, data=data)
    if responseFormat is None:
        return response
    return formatMapping[responseFormat.lower()](response.content.decode('utf-8'))


def buildUrl(url, params, headers, method='get'):
    return Request(method, url, params=params, headers=headers).prepare().url
