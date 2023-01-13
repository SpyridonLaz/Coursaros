
from ItemCollector import *
from Platform.Platform import *
from Urls.EdxUrls import EdxUrls as const

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class Course(const):
    def __init__(self,context:Platform, slug :str=None ,  BASE_FILEPATH=  Path.home()):
        self._client = context.client
        self._collector = context.collector
        self.headers= context.headers
        self.platform = context.platform
        self._slug= slug
        self._course_dir = slug
        self._BASE_FILEPATH = self.BASE_FILEPATH(BASE_FILEPATH)
        self._collector = Collector()

    @property
    def BASE_FILEPATH(self):
        return self._BASE_FILEPATH

    @BASE_FILEPATH.setter
    def BASE_FILEPATH(self, value):
        path = Path(self.BASE_FILEPATH,self.platform)
        if not path.exists():
            value.mkdir(parents=True, exist_ok=True)

        self._BASE_FILEPATH = value

    @property
    def client(self):
        return self._client
    @property
    def collector(self):
        return self._collector


    @property
    def slug(self):
        return self._slug


    @slug.setter
    def slug(self, slug:str):
        self._slug = slug

    @property
    def url(self):
        return self.url

    @url.setter
    def url(self, url):
        self.url = url

    @property
    def course_dir(self):
        return self._course_dir
    @course_dir.setter
    def course_dir(self, value):
        self._course_dir = value

