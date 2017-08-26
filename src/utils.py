import json
import requests
import untangle


def postResponse(url, params, headers):
    response = requests.post(url, headers, params)
    return response.content.decode('utf-8')


def _getResponse(url, params, headers):
    response = requests.get(url, headers=headers, params=params)
    return response.content.decode('utf-8')


def getJSONResponse(url, params, headers):
    return json.loads(_getResponse(url, params, headers))


def getXMLResponse(url, params, headers):
    return untangle.parse(_getResponse(url, params, headers))
