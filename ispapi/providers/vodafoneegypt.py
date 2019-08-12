import time
import requests
from .provider import Provider, Quota

LOGINURL = "https://web.vodafone.com.eg/services/security/oauth/oauth/token"
QUOTAURL = "https://web.vodafone.com.eg/services/mi/getQuota"


class VodafoneEgypt(Provider):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.username = username
        self.password = password
        self.session = requests.Session()


    def _login(self):
        data = {'username': self.username, 'password': self.password,
                'grant_type': 'password', 'client_id': 'my-trusted-client',
                'client_secret': 'secret'}
        for attempt in range(3):
            try:
                resp = self.session.post(LOGINURL,  data=data, headers={'api-host': 'token'})
                break
            except:
                if attempt >= 2:
                    raise
        resp.raise_for_status()
        respdata = resp.json()
        self.session.headers['access-token'] = respdata['access_token']
        self.session.headers['msisdn'] = self.username
        return respdata

    def _get_quota(self):
        resp = self.session.post(QUOTAURL, json={"msisdn": self.username}, headers={'api-host': 'MobileInternetHost', "Referer": "https://web.vodafone.com.eg/en/redmanagement"})
        resp.raise_for_status()
        respdata = resp.json()
        for package in respdata["quotaDTO"]:
            try:
                renewdate = time.mktime(time.strptime(package["renewalDate"], "%d-%b-%y"))
                break
            except ValueError:
                renewdate = time.time()

        quota = Quota(renewdate, respdata["totalBalance"] * 1024, respdata["totalConsumption"] * 1024)
        return quota
