from abc import ABC

from fake_useragent import UserAgent


class PlatformUrls(ABC):

    _platform = None
    _LMS_BASE_URL = None
    _BASE_API_URL = None
    _LOGIN_URL = None
    _COURSE_BASE_URL = None
    _COURSE_OUTLINE_BASE_URL = None
    _LOGIN_API_URL = None
    _DASHBOARD_URL = None
    _headers = None
    def __init__(self, HOSTNAME,):
        self.HOSTNAME = HOSTNAME

        self._PROTOCOL_URL = 'https://{}'.format(self.HOSTNAME)


    @property
    def HOSTNAME(self):
        return self._HOSTNAME

    @HOSTNAME.setter
    def HOSTNAME(self, value):
        self._HOSTNAME = value
    @property
    def platform(self):
        return self._platform


    @property
    def headers(self):
        self._headers['user-agent'] = UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome
        return self._headers

    def cookie(self, cookieJar):
        # Load the cookie to the headers
        new = cookieJar.get('csrftoken', None)
        # older versions
        old = cookieJar.get('csrf', None)
        self._headers['x-csrftoken'] = new if new else old

    @headers.setter
    def headers(self,*args,):
        self._headers.update({args[0]:args[1]})

    @property
    def PROTOCOL_URL(self):
        return self._PROTOCOL_URL

    @property
    def LMS_BASE_URL(self):
        return self._LMS_BASE_URL

    @property
    def BASE_API_URL(self):
        return self._BASE_API_URL

    @property
    def LOGIN_URL(self):
        return self._LOGIN_URL

    @property
    def COURSE_BASE_URL(self):
        return self._COURSE_BASE_URL



    @property
    def LOGIN_API_URL(self):
        return self._LOGIN_API_URL

    @property
    def DASHBOARD_URL(self):
        return self._DASHBOARD_URL




