import requests
import copy
import time
import base64
import json

from .provider import Provider, Quota

TOKENURL = 'https://api-my.te.eg/api/user/generatetoken?channelId=WEB_APP'
STATUSURL = 'https://api-my.te.eg/api/user/status'
LOGINURL = 'https://api-my.te.eg/api/user/login?channelId=WEB_APP'
DATAURL = 'https://api-my.te.eg/api/line/freeunitusage'

STATUSDATA = {
  "header": {
    "timestamp": 0,
    "customerId": "",
    "msisdn": "",
    "messageCode": "",
    "locale": "En"
  },
  "body": {}
}

LOGINDATA = {
  "header": {
    "msisdn": "",
    "timestamp": "",
    "locale": "En"
  },
  "body": {
    "password": ""
  }
}

def basedecode(data):
    rem = len(data) % 4
    if rem > 0:
        data += "=" * (4 - rem)
    return json.loads(base64.urlsafe_b64decode(data))

def is_jwt_expired(jwt):
    header, data, signature = jwt.split('.')
    ddata = basedecode(data)
    return ddata['exp'] - 60 < time.time()


class TelecomEgypt(Provider):
    def __init__(self, username, password):
        """AD"""
        super().__init__(username, password)
        self.username  = username
        self.customerId = None
        self.password = password
        self.session = requests.Session()

    def _login(self):
        resp = self.session.get(TOKENURL)
        responsedata = self._validate_response(resp, 'Failed to get token')
        self.session.headers['Jwt'] = responsedata['body']['jwt']

        statusdata = copy.deepcopy(STATUSDATA)
        statusdata['header']['msisdn'] = self.username
        resp = self.session.post(STATUSURL, json=statusdata)
        responsedata = self._validate_response(resp, 'Failed to get status')
        
        logindata = copy.deepcopy(LOGINDATA)
        logindata['header']['msisdn'] = self.username
        logindata['header']['timestamp'] = str(responsedata['header']['timstamp'])
        logindata['body']['password'] = self.password
        resp = self.session.post(LOGINURL, json=logindata)
        responsedata = self._validate_response(resp, 'Failed to login')
        self.session.headers['Jwt'] = responsedata['body']['jwt']
        self.customerId = responsedata['header']['customerId']

    def _validate_response(self, response, message):
        response.raise_for_status()
        responsedata = response.json()
        if str(responsedata['header']['responseCode']) != "0":
            raise RuntimeError('{}: {}'.format(message, responsedata['header']['responseMessage']))
        return responsedata

    def _get_quota(self):
        if is_jwt_expired(self.session.headers['Jwt']):
            self.login()
        postdata = {
            'header': {
                'customerId': self.customerId,
                'msisdn': self.username,
                'locale': 'En'
            },
            'body': {}
        }
        resp = self.session.post(DATAURL, json=postdata)
        respdata = self._validate_response(resp, 'Failed to get data')
        for bundle in respdata['body']['detailedLineUsageList']:
            if bundle['remainingDaysForRenewal'] != 0:
                break
        endtime = time.time() + bundle['remainingDaysForRenewal'] * 24 * 3600
        return Quota(endtime, bundle['initialTotalAmount'] * 1024 ** 2, bundle['usedAmount'] * 1024 ** 2)
