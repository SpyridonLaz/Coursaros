from abc import ABC
from pathlib import Path

import pdfkit

from ItemCollector import Collector
from Platform import AbstractPlatform


try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class Course(ABC, Collector):

    def __init__(self,context:AbstractPlatform, slug :str=None   ):
        self._client = context.client
        # Collects scraped items and separates them from those already found.
        # Prevents unescessary crawling
        self.headers= context.headers
        self.SAVE_TO = context.SAVE_TO
        super(Collector).__init__(SAVE_TO=self.SAVE_TO)

        self._course_title = None
        self._course_dir = None
        self._collector = context.Collector()

        self._slug= slug

    @property
    def course_title(self):
        return self._course_title
    @property
    def course_dir(self):
        return self._course_dir

    @course_dir.setter
    def course_dir(self, value):
        path = Path(self.SAVE_TO, value)
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