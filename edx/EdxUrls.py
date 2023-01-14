from Urls import PlatformUrls


class EdxUrls(Urls):
    # Base URLs as pseudo constants
    def __init__(self, HOSTNAME):
        super(Urls).__init__(HOSTNAME)
        self._PROTOCOL_URL = 'https://{}'.format(HOSTNAME)
        self._BASE_API_URL = '{}/api'.format(self.PROTOCOL_URL)
        self._LOGIN_URL = '{}/login'.format(self.PROTOCOL_URL)
        self._COURSE_BASE_URL = '{}/courses'.format(self.PROTOCOL_URL)
        self._COURSE_OUTLINE_BASE_URL = '{}/course_home/v1/outline'.format(self.BASE_API_URL)
        self._XBLOCK_BASE_URL = '{}/xblock'.format(self.PROTOCOL_URL)
        self._LOGIN_API_URL = '{}/user/v1/account/login_session/'.format(self.BASE_API_URL)
        self._DASHBOARD_URL = '{}/dashboard/'.format(self.PROTOCOL_URL)

    @property
    def COURSE_OUTLINE_BASE_URL(self):
        return self._COURSE_OUTLINE_BASE_URL

    @property
    def XBLOCK_BASE_URL(self):
        return self._XBLOCK_BASE_URL



