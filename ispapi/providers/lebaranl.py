from .provider import Provider
import requests
from bs4 import BeautifulSoup

import re

LOGIN_FORM_URL = 'https://mobile.lebara.com/nl/en/login'
LOGIN_URL = 'https://mobile.lebara.com/nl/en/j_spring_security_check'
DASHBOARD_URL = 'https://mobile.lebara.com/nl/en/my-mobile/dashboard'

BS4_PARSER = 'html.parser'

class LebaraNL(Provider):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookies = None

        # for caching
        self.page = None

    @staticmethod
    def cleanup_string(s):
        return re.sub(r'\s+|\xa0', ' ', s.strip())

    def login_internal(self):
        login_form = requests.get(LOGIN_FORM_URL)
        login_form_b = BeautifulSoup(login_form.text, features=BS4_PARSER)
        csrf_elem = login_form_b.find(attrs={'id': 'lebaraLoginForm'}).find(attrs={'name': 'CSRFToken'})
        csrf = csrf_elem.attrs['value']

        login = requests.post(LOGIN_URL, data={'j_username': self.email, 'j_password': self.password, 'CSRFToken': csrf})
        if login.status_code >= 400:
            raise RuntimeError("login failed most probably invalid username or password, status code %d"%(login.status_code))
        self.cookies = login.cookies
        self.page = login.text
        return dict(self.cookies)

    def get_quota_internal(self):
        if self.page is None:
            dashboard = requests.get(DASHBOARD_URL, cookies=self.cookies)
            self.page = dashboard.text
        page = BeautifulSoup(self.page, features=BS4_PARSER)
        allowances = page.find(text='Allowances')
        if allowances is None:
            # retry in dutch
            allowances = page.find(text='Tegoed')
        
        if allowances is None:
            raise RuntimeError("unable to find available package")
        allowances_table = allowances.parent.parent.parent
        
        result = {
            LebaraNL.cleanup_string(e.find_all('td')[0].text): LebaraNL.cleanup_string(e.find_all('td')[1].text)
                for e in allowances_table.find_all('tr')[1:]
        }
        result['balance'] = page.find(class_='dashboard-current-balance').text
        return result