import requests
import copy
import time
import base64
import json

from .provider import Provider, Quota

TOKENURL = 'https://api-my.te.eg/api/user/generatetoken?channelId=WEB_APP'
LOGINURL = 'https://api-my.te.eg/api/user/login?channelId=WEB_APP'
DATAURL = 'https://api-my.te.eg/api/line/freeunitusage'

LOGINDATA = {
  "header": {
    "msisdn": "",
    "timestamp": "",
    "locale": "en"
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

        logindata = copy.deepcopy(LOGINDATA)
        logindata['header']['msisdn'] = self.username
        logindata['header']['timestamp'] = str(int(time.time()))
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
        endtime = time.time()  # now
        initialTotalAmount = 0
        usedAmount = 0
        for bundle in respdata['body']['detailedLineUsageList']:
            endtimebundle = time.mktime(time.strptime(bundle['renewalDate'], "%Y-%m-%d"))
            if endtimebundle > endtime:
                # it expired end of the day
                endtime = endtimebundle + 24 * 3600
            initialTotalAmount += bundle['initialTotalAmount']
            usedAmount += bundle['usedAmount']
        return Quota(endtime, initialTotalAmount * 1024 ** 3, usedAmount * 1024 ** 3)
