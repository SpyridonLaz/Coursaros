from Urls.PlatformUrls import PlatformUrls


class EdxUrls(PlatformUrls):
    # Base URLs as pseudo constants
    HOSTNAME = 'courses.edx.org'
    platform = 'Edx'
    def __init__(self,):

        super().__init__(self.HOSTNAME)
        self._BASE_API_URL = f'{self.PROTOCOL_URL}/api'
        self._LOGIN_URL = f'{self.PROTOCOL_URL}/login'
        self._COURSE_BASE_URL = f'{self.PROTOCOL_URL}/courses'
        self._COURSE_OUTLINE_BASE_URL = f'{self.BASE_API_URL}/course_home/v1/outline'
        self._XBLOCK_BASE_URL = f'{self.PROTOCOL_URL}/xblock'
        self._LOGIN_API_URL = f'{self.BASE_API_URL}/user/v1/account/login_session/'
        self._DASHBOARD_URL = f'{self.PROTOCOL_URL}/dashboard/'


        #  Some headers may not be required
        # but sending all is a good practice.

        self._headers = {
            'Host': self.HOSTNAME,
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': None,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': self.PROTOCOL_URL,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.LOGIN_URL,
            'accept-language': 'en-US,en;q=0.9',
        }


    @property
    def COURSE_OUTLINE_BASE_URL(self):
        return self._COURSE_OUTLINE_BASE_URL

    @property
    def XBLOCK_BASE_URL(self):
        return self._XBLOCK_BASE_URL



