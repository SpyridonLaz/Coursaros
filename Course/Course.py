
from ItemCollector import *
from Platform.Platform import *
from edx.EdxUrls import EdxUrls as const

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class Course:

    def __init__(self,context:Platform, slug :str=None   ):
        self._client = context.client
        # Collects scraped items and separates them from those already found.
        # Prevents unescessary crawling
        self.headers= context.headers
        self.platform = context.platform
        self.SAVE_TO = context.SAVE_TO

        self._course_title = None
        self._course_dir = None
        self._collector = context.Collector(SAVE_TO=context.SAVE_TO)

        self._slug= slug

    @property
    def course_title(self):
        return self._course_title





    @property
    def course_dir(self):
        return self._course_dir

    @course_dir.setter
    def course_dir(self, value):
        path = Path(self.SAVE_TO,value)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self._course_dir = path

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

