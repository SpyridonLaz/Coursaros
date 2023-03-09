from Urls.platform_urls import PlatformUrls


class EdxUrls(PlatformUrls):
    # Base URLs as pseudo constants
    ROOT = 'edx'
    TOP_DOM = 'org'
    DOMAIN = f'{ROOT}.{TOP_DOM}'
    platform = 'Edx'
    def __init__(self,):

        super().__init__(self.DOMAIN)
        self._COURSE_BASE_URL = self.BASE_HOSTNAME.format(sub='courses', resource ="/{resource}")

        self._LOGIN_URL = self.COURSE_BASE_URL.format( resource ="login")


        self._API_BASE_URL = self.COURSE_BASE_URL.format(resource = "api/{}")
        "course-v1:LinuxFoundationX+LFS170x+2T2021"

        self._LOGIN_API_URL = self.API_BASE_URL.format("user/v1/account/login_session/")


        self._COURSE_OUTLINE_BASE_URL = self.API_BASE_URL.format("course_home/v2/outline/{slug}")

        self.API_DOCS_URL = self.COURSE_BASE_URL.format(resource = "api-docs/")
        self._XBLOCK_BASE_URL = self.COURSE_BASE_URL.format(resource = 'xblock')

        self._DASHBOARD_URL = self.BASE_HOSTNAME.format(
            sub='home',
            resource = ""
        )

        self._DASHBOARD_API_URL = self.API_BASE_URL.format("enrollment/v1/enrollment")

        #  Some headers may not be required
        # but sending all is a good practice.
        self.ua = self.user_agent()
        self._headers = {
            'Host': "courses."+self.DOMAIN,
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': self.ua,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'origin': self.COURSE_BASE_URL.format( resource =""),
            'Referer': self.LOGIN_API_URL,
            'accept-language': 'en-US,en;q=0.9',
        }


    @property
    def COURSE_OUTLINE_BASE_URL(self):
        return self._COURSE_OUTLINE_BASE_URL

    @property
    def XBLOCK_BASE_URL(self):
        return self._XBLOCK_BASE_URL




    @property
    def LOGIN_API_URL(self):
        return self._LOGIN_API_URL

    @property
    def DASHBOARD_API_URL(self):
        return self._DASHBOARD_API_URL