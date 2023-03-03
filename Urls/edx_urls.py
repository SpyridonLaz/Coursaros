from Urls.platform_urls import PlatformUrls


class EdxUrls(PlatformUrls):
    # Base URLs as pseudo constants
    ROOT = 'edx'
    TOP_DOM = 'org'
    DOMAIN = f'{ROOT}.{TOP_DOM}'
    platform = 'Edx'
    def __init__(self,):

        super().__init__(self.DOMAIN)
        print(self.BASE_HOSTNAME)
        self._LOGIN_URL = self.BASE_HOSTNAME.format(sub='authn', resource = "login")
        self._COURSE_BASE_URL = self.BASE_HOSTNAME.format(sub='courses', resource ="{resource}")


        self._BASE_API_URL = self._COURSE_BASE_URL.format(resource = "api")


        self._COURSE_OUTLINE_BASE_URL = f'{self.BASE_API_URL}/course_home/v1/outline/'

        self._XBLOCK_BASE_URL = self._COURSE_BASE_URL.format(resource = '/xblock')
        self._LOGIN_API_URL = f'{self.BASE_API_URL}/user/v1/account/login_session/'

        self._DASHBOARD_URL = self.BASE_HOSTNAME.format(
            sub='home',
            resource = ""
        )
        print(self._DASHBOARD_URL)

        #  Some headers may not be required
        # but sending all is a good practice.

        self._headers = {
            'Host': self.DOMAIN,
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': self.user_agent(),
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
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



