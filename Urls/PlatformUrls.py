from pathlib import Path



class PlatformUrls:

    def __init__(self, HOSTNAME ,):
        self._HOSTNAME = HOSTNAME
        self._platform = None
        self._PROTOCOL_URL = 'https://{}'.format(self.HOSTNAME)
        self._LMS_BASE_URL = None
        self._BASE_API_URL = None
        self._LOGIN_URL = None
        self._COURSE_BASE_URL = None
        self._COURSE_OUTLINE_BASE_URL = None
        self._LOGIN_API_URL = None
        self._DASHBOARD_URL = None





    @property

    def HOSTNAME(self):
        return self._HOSTNAME
    @property
    def platform(self):
        return self._platform





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


pass



# class CollectorUrls:
#
#     def __init__(self ,   SAVE_AS ):
#         self.SAVE_AS
#         self.pdf_results = self.SAVE_AS.as_uri().format(file='.PDFResults')
#
#         self.results = self.SAVE_AS.as_uri().format(file='.Results')
#         self.negative_results = self.SAVE_AS.as_uri().format(file='.Results_bad')
