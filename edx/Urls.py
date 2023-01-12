from pathlib import Path


class EdxUrls:
    # Base URLs as pseudo constants

    _HOSTNAME = 'courses.edx.org'

    @property
    @classmethod
    def HOSTNAME(cls):
        return cls._HOSTNAME

    _PROTOCOL_URL = 'https://{}'.format(_HOSTNAME)

    @property
    @classmethod
    def PROTOCOL_URL(cls):
        return cls._PROTOCOL_URL



    _LMS_BASE_URL = 'https://learning.edx.org'

    @property
    @classmethod
    def LMS_BASE_URL(cls):
        return cls._LMS_BASE_URL
    _BASE_API_URL = '{}/api'.format(_PROTOCOL_URL)

    @property
    @classmethod
    def BASE_API_URL(cls):
        return cls._BASE_API_URL
    _LOGIN_URL = '{}/login'.format(_PROTOCOL_URL)

    @property
    @classmethod
    def LOGIN_URL(cls):
        return cls._LOGIN_URL
    _COURSE_BASE_URL = '{}/courses'.format(_PROTOCOL_URL)

    @property
    @classmethod
    def COURSE_BASE_URL(cls):
        return cls._COURSE_BASE_URL
    _COURSE_OUTLINE_BASE_URL = '{}/course_home/v1/outline'.format(_BASE_API_URL)

    @property
    @classmethod
    def COURSE_OUTLINE_BASE_URL(cls):
        return cls._COURSE_OUTLINE_BASE_URL
    _XBLOCK_BASE_URL = '{}/xblock'.format(_PROTOCOL_URL)

    @property
    @classmethod
    def XBLOCK_BASE_URL(cls):
        return cls._XBLOCK_BASE_URL

    _LOGIN_API_URL = '{}/user/v1/account/login_session/'.format(_BASE_API_URL)

    @property
    @classmethod
    def LOGIN_API_URL(cls):
        return cls._LOGIN_API_URL
    _DASHBOARD_URL = '{}/dashboard/'.format(_PROTOCOL_URL)

    @property
    @classmethod
    def DASHBOARD_URL(cls):
        return cls._DASHBOARD_URL

    _SAVED_SESSION_PATH = Path.joinpath(Path(), '.edxcookie')

    @property
    @classmethod
    def SAVED_SESSION_PATH(cls):
        return cls._SAVED_SESSION_PATH




class EdxKaltura(EdxUrls):
    _BASE_KALTURA_VIDEO_URL = "https://cdnapisec.kaltura.com/p/{PID}/sp/{PID}00/playManifest/entryId/{entryId}/format/download/protocol/https/flavorParamIds/0"

    @property
    @classmethod
    def BASE_KALTURA_VIDEO_URL(self):
        return self._BASE_KALTURA_VIDEO_URL



    # @property
    # def COURSE_OUTLINE_BASE_URL(self: Edx):
    #     return self.COURSE_OUTLINE_BASE_URL

