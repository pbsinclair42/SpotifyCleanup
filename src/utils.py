from json import loads as parseJson
from requests import request, Request
from untangle import parse as parseXml


def httpRequest(url, params, headers, method='get', responseFormat='json'):
    formatMapping = {'json': parseJson, 'xml': parseXml, None: None}

    if responseFormat not in formatMapping.keys():
        raise ValueError("Unknown format " + responseFormat)

    response = request(method, url=url, headers=headers, params=params)
    if responseFormat is None:
        return response
    return formatMapping[responseFormat.lower()](response.content.decode('utf-8'))

def buildUrl(url, params, headers, method='get'):
    return Request(method, url, params=params, headers=headers).prepare().url