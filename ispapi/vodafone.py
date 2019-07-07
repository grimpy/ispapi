import requests

LOGINURL = "https://web.vodafone.com.eg/services/security/oauth/oauth/token"
QUOTAURL = "https://web.vodafone.com.eg/services/mi/getQuota"


class Vodafone:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()


    def login(self):
        data = {'username': self.username, 'password': self.password,
                'grant_type': 'password', 'client_id': 'my-trusted-client',
                'client_secret': 'secret'}
        resp = self.session.post(LOGINURL,  data=data, headers={'api-host': 'token'})
        resp.raise_for_status()
        respdata = resp.json()
        self.session.headers['access-token'] = respdata['access_token']
        self.session.headers['msisdn'] = self.username
        return respdata

    def get_quota(self):
        resp = self.session.post(QUOTAURL, json={"msisdn": self.username}, headers={'api-host': 'MobileInternetHost', "Referer": "https://web.vodafone.com.eg/en/redmanagement"})
        resp.raise_for_status()
        respdata = resp.json()
        return respdata

if __name__ == '__main__':
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    options = parser.parse_args()

    vf = Vodafone(options.user, options.password)
    print(vf.login())
    print(vf.get_quota())
