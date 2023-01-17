from abc import ABC
from pathlib import Path

import pdfkit

from ItemCollector import Collector
from Platforms.Platform import BasePlatform

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class BaseCourse(ABC, ):

    def __init__(self, context:BasePlatform, slug :str=None):
        self._client = context.client
        # Prevents unescessary crawling
        self.urls= context.urls
        self._course_title = None
        self._course_dir = None
        self._slug= slug


    @property
    def SAVE_TO(self):
        return self._SAVE_TO
    @SAVE_TO.setter
    def SAVE_TO(self, course_dir):
        path = Path(course_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self._SAVE_TO = path

    @property
    def course_title(self)->Path :
        return self._course_title

    @course_title.setter
    def course_title(self,title):
        self._course_title = title
        self.course_dir = self.course_title
        if not self.collector:
            self._collector = Collector(self.course_dir)
        else:
            self.collector.SAVE_TO(self.course_dir)
    @property
    def collector(self):
        return self._collector


    @property
    def course_dir(self) ->Path :

        return self._course_dir

    @course_dir.setter
    def course_dir(self, value):
        path = Path(self.SAVE_TO, value)

        if not path.exists():
            if self.course_dir.exists():
                self.course_dir.rename(path)
            else:
                path.mkdir(parents=True, exist_ok=True)

        self._course_dir = path

    @property
    def client(self):
        return self._client


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

    def save_as_pdf(self, content: str, path: str, id: str):
        '''
        :param content: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        pdf_save_as = Path(path)
        pdfkit.from_string(content, output_path=pdf_save_as)
        self.collector.pdf_results_id.add(id)