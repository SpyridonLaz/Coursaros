from abc import ABC
from pathlib import Path
import re

import pdfkit

from ItemCollector import Collector

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class BaseCourse(ABC, ):

    def __init__(self,
                context,
                 slug :str=None,
                 title :str=None,):

        self.urls = context.urls
        self._connector = context.connector
        self._save_to = context.save_to
        self._course_dir = Path(slug)
        self._slug = slug
        self._collector = None

        if title:
            self.course_title = title



    @property
    def save_to(self):
        return self._save_to
    @save_to.setter
    def save_to(self, course_dir):
        path = Path(course_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self._save_to = path
    def sanitizer(self, string ):
        return re.sub(r'[^\w_ ]', '-', string).replace('/', '-').strip()
    @property
    def course_title(self) :
        return self._course_title

    @course_title.setter
    def course_title(self,title):
        self._course_title = self.sanitizer(title)
        self.course_dir = self._course_title
        print(self.course_dir)
        if  self._collector:
            self.collector.save_to(self.course_dir)
        else:
            self._collector = Collector(self.course_dir)

    @property
    def collector(self):
        return self._collector


    @property
    def course_dir(self) ->Path :

        return self._course_dir

    @course_dir.setter
    def course_dir(self, value):
        path = Path(self._save_to, value)

        if not path.exists():
            if self._course_dir.exists():
                self.course_dir.rename(path)
            else:
                path.mkdir(parents=True, exist_ok=True)

        self._course_dir = path

    @property
    def connector(self):
        return self._connector


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

    def get_pdf(self, content: str, path: str, id: str):
        '''
        :param content: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        pdf_save_as = Path(path)
        pdfkit.from_string(content, output_path=pdf_save_as)
        self.collector.pdf_results_id.add(id)