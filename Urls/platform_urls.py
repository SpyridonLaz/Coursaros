from abc import ABC

import requests
from fake_useragent import UserAgent


class PlatformUrls(ABC):

    _platform = None
    _PROTOCOL_URL = 'https'
    _LMS_BASE_URL = None
    _API_BASE_URL = None
    _LOGIN_URL = None
    _COURSE_BASE_URL = None
    _COURSE_OUTLINE_BASE_URL = None
    _DASHBOARD_URL = None
    _headers = None
    _DOMAIN = None
    build_url = '{protocol}://{sub}.{domain}{resource}'.format

    def __init__(self, DOMAIN,):
        self._DOMAIN = DOMAIN

        self.BASE_HOSTNAME = self.build_url(
                        protocol=self.PROTOCOL_URL,
                        sub='{sub}',
                        domain=self.DOMAIN,
                        resource='{resource}'
                        )
    @property
    def DOMAIN(self):
        return self._DOMAIN


    @property
    def platform(self):
        return self._platform


    @property
    def headers(self):
         return self._headers

    def user_agent(self):
        ua =UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome

        return ua
    def csrf_to_headers(self, client:requests.Session ,):
        # Load the cookie to the headers
        new = client.cookies.get('csrftoken', None)
        # older versions
        old = client.cookies.get('csrf', None)
        csrf_token = {"x-csrftoken":new or old}
        client.headers.update(csrf_token)
        self.headers = csrf_token

    @headers.setter
    def headers(self,*headers,):
        for header in headers:
            self._headers.update(header)

    @property
    def PROTOCOL_URL(self):
        return self._PROTOCOL_URL

    @property
    def LMS_BASE_URL(self):
        return self._LMS_BASE_URL

    @property
    def API_BASE_URL(self):
        return self._API_BASE_URL

    @property
    def LOGIN_URL(self):
        return self._LOGIN_URL

    @property
    def COURSE_BASE_URL(self):
        return self._COURSE_BASE_URL



    @property
    def DASHBOARD_URL(self):
        return self._DASHBOARD_URL

