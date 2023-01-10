from pathlib import Path


class BaseEdxUrls:
   
   
   # Base URLs as pseudo constants
    EDX_HOSTNAME = 'courses.edx.org'
    BASE_URL = 'https://{}'.format(EDX_HOSTNAME)
    LMS_BASE_URL = 'https://learning.edx.org'
    BASE_API_URL = '{}/api'.format(BASE_URL)
    LOGIN_URL = '{}/login'.format(BASE_URL)
    COURSE_BASE_URL = '{}/courses'.format(BASE_URL)
    COURSE_OUTLINE_BASE_URL = '{}/course_home/v1/outline'.format(BASE_API_URL)
    _XBLOCK_BASE_URL = '{}/xblock'.format(BASE_URL)
    LOGIN_API_URL = '{}/user/v1/account/login_session/'.format(BASE_API_URL)
    DASHBOARD_URL = '{}/dashboard/'.format(BASE_URL)
    
    BASE_FILEPATH = Path(Path().home(), '{file}')
    SAVED_SESSION_PATH = Path.joinpath(Path(), '.edxcookie')


    @property
    def XBLOCK_BASE_URL(self):
        return self._XBLOCK_BASE_URL