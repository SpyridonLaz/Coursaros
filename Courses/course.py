from abc import ABC
from pathlib import Path
import re
import pdfkit
from item_collector import Collector



class BaseCourse(ABC,Collector ):

    def __init__(self, context, slug: str = None, title: str = None):

        self.context = context
        self.urls = context.urls
        self._client = context.client
        self._save_to = context.save_to
        self._slug = None

        self._course_dir = Path(slug)

        if title:
            self.title = title
        super().__init__(save_to=self.course_dir)



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
    def title(self) :
        return self._title

    @title.setter
    def title(self,title):
        self._title = self.sanitizer(title)
        self.course_dir = self._title


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

    def get_pdf(self, content: str,check, path: str|Path, id: str):
        '''
        :param content: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        path = Path(path).with_suffix('.pdf')
        if check and not path.exists():

            _content = content.replace('src="',
                                       f'src="{self.urls.PROTOCOL_URL}/')
            _content = _content.replace(f'src="{self.urls.PROTOCOL_URL}/http',
                                         'src="http')

            pdfkit.from_string(_content, output_path=path)
            self.context.pdf_results_id.add(id)
            print("PDF saved!", "orange")
            return True
        else: return False