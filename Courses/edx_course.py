import html
import json
import sys
import time
import lxml
import traceback
from collections import deque
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import validators
from bs4 import BeautifulSoup
from exceptions import EdxRequestError, EdxInvalidCourseError, EdxNotEnrolledError
from Courses.course import BaseCourse

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt

    log = log()
    d = d()
except ImportError:
    log = print
    d = print
    pass


class EdxCourse(BaseCourse, ):

    def __init__(self, context,
                 slug: str,
                 title: str ):
        super().__init__(context=context,
                         slug=slug,
                         title=title)
        self.silent = None
        self.context = context
        self.slug = slug
        self.xblocks = None
        self.lectures = None
        self.chapters = None
        self.downloads = deque()
        self.title = title

    def add_item(self, item):
        self.downloads.append(item)

    @BaseCourse.slug.setter
    def slug(self, slug: str):
        self._slug = slug
        import requests
        self.outline_url = self.urls.COURSE_OUTLINE_BASE_URL.format(slug=requests.utils.quote(slug))
        print(self.slug,self.outline_url)

    @BaseCourse.url.setter
    def url(self, url):
        '''
         This method expects a course_dir's URL as argument,
          searches for it's xBlock structure and, if found,
           it returns it as a dictionary,else raises exception.
        '''

        log('Building xblocks.')
        # TODO  URL CHECK START
        # Break down the given course URL to get the course_dir slug.
        if validators.url(url):
            for part in url.split('/'):
                if part.startswith('course-'):
                    self.slug = part
                    return
        else:
            # If the conditions above are not passed, we will assume that a wrong
            # course_dir URL was passed in.
            raise EdxInvalidCourseError('The provided course URL seems to be invalid.')

        # if course_slug in self.collector.negative_results_id:
        # 	return

    @BaseCourse.title.setter
    def title_alt(self, blocks):
        if blocks[0].get('type') == 'course' and blocks[0].get('display_name') is not None:
            course_dir_name = self.sanitizer(blocks[0].get('display_name'))
            super().title = course_dir_name

        else:
            for block, block_meta in blocks.items():
                if block_meta.get('type') == 'course' and block_meta.get('display_name') is not None:
                    course_dir_name = block_meta.get('display_name')
                    super().title = self.sanitizer(course_dir_name)
        # if course_slug in self.collector.negative_results_id:
        # 	return

    def _get_xblocks(self,):
        # Construct the course_dir outline URL

        # We make an HTTP GET request to outline URL api
        # and return a json object
        # with xblocks:metadata which
        # will allow us to map the course_dir.

        try:
            self.context.driver.get(self.outline_url)
            text = WebDriverWait(self.context.driver, 4).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))).text
            convert_resp = json.loads(text)
        except ConnectionError as e:
            raise EdxRequestError(e)
        except TimeoutException as e:
            print(e)
            if not self.silent:
                return

            raise EdxInvalidCourseError('The provided course URL seems to be invalid. Check the URL and try again.')

        # course_dir's xblock structure.
        # blocks:metadata as keys:values
        # print("OUTLINE RESP: ", self.context.driver)
        # blocks = json.loads(self.context.driver)
        # find("//div[contains(@class,'ic--card') and not(contains(@class,'off'))]")
        xblocks = convert_resp.get('course_blocks', None)
        if isinstance(xblocks, dict) and xblocks.get('blocks', None):
            self.xblocks = xblocks.get('blocks')
            return True
        else:
            # If no blocks are found, we will assume that
            # the user has no access to the course_dir.
            # Not authorized, not enrolled, course locked, etc.
            raise EdxNotEnrolledError(
                'No course_dir content was found. Check the availability of the course_dir and try again.')

    def _separate_xblocks(self, ):

        self.lectures = {k: v for k, v in self.xblocks.items() if v['type'] == 'sequential'}
        self.chapters = {k: v for k, v in self.xblocks.items() if v['type'] == 'chapter' and v['children'] is not None}
        return self.chapters and self.lectures
    def build_dir_tree(self):
        self._get_xblocks()
        self._separate_xblocks()

        print("Building directory tree for {}...".format(self.title))

        # assuming that lectures are ordered
        for i, (lecture, lecture_meta) in enumerate(self.lectures.items()):
            lecture_name = lecture_meta.get('display_name')
            lecture_name = self.sanitizer(lecture_name)

            for chapter, chapter_meta in self.chapters.items():
                if lecture in chapter_meta.get('children'):
                    chapter_name = self.sanitizer(chapter_meta.get('display_name'))
                    chapter_dir = Path(self.course_dir, chapter_name)

                    path = Path(chapter_dir, lecture_name)
                    lecture_meta.update({'chapterID': chapter_meta.get('id')})
                    lecture_meta.update({'path': path})
        print("..built.")


    def walk(self, ):
        self.build_dir_tree()
        self.main_iterator()

    def main_iterator(self):

        # mallon sto platform
        for i, (lecture, lecture_meta) in enumerate(self.lectures.items()):
            lecture_url = self.urls.XBLOCK_BASE_URL.format(url= lecture)
            print(lecture_url)
            soup = None
            for j in range(3):
                try:
                    self.context.driver.get(lecture_url,   )
                    soup = BeautifulSoup(self.context.driver.page_source, 'lxml')
                except Exception as e:
                    print("Error: ", e)
                    if j == 2:
                        raise EdxRequestError(e)

                    continue
                else:
                    break

            try:

                # KalturaScraper(lecture, lecture_meta, soup)

                self.scrape(lecture, lecture_meta, soup)
            except (KeyboardInterrupt, ConnectionError):

                self.context.save()

            # //TODO  με pandas και με DINJECTION
            self.context.negative_results_id.add(lecture)
        else:
            self.context.negative_results_id.add(self.slug)
        self.context.save()

    def scrape(self, lecture, lecture_meta, soup):
        '''
        # Searches through HTML elements
        # Finds and builds URLs for subtitles and videos
        '''

        for elem in soup.find_all('div', {'class': 'xblock-student_view-video'}):

            header_block = elem.find('h3', attrs={'class': 'hd hd-2'})
            if header_block:
                segment = self.sanitizer(header_block.text)
                _name = lecture_meta.get('path')
                name = f'{segment} - ' + _name.name
                filepath = Path(_name.parent, name)
                lecture_meta.update({'filepath': filepath})

                paragraphs = elem.find_all('p')
                print("PDF URL CONTENT IS HERE4 :", elem.decode_contents())

                inner_html = elem.decode_contents().replace('src="',
                                                            f'src="{self.urls.COURSE_BASE_URL}')
                print("PDF URL CONTENT IS HERE5 :", inner_html)

                inner_html = inner_html.replace(f'src="{self.urls.COURSE_BASE_URL}/http', 'src="http')
                print("PDF URL CONTENT IS HERE6 :", inner_html)

                try:

                    self.context.get_pdf(content=inner_html,
                                         check=paragraphs,
                                         path=filepath,
                                         id=lecture)
                except Exception as e:
                    print("Problem while building PDF.")
                    print(e)

                meta_block = elem.find('div', {'class': 'video', 'data-metadata': True})
                if meta_block:
                    json_meta = json.loads(meta_block.get('data-metadata'))
                    # Get the data-metadata attribute HTML
                    # and parse it as a JSON object.
                    if 'sources' in json_meta:
                        for video_source in list(json_meta['sources']):
                            if video_source.endswith('.mp4'):
                                # video URL found
                                log(f"Struck gold! A video was found in segment: {filepath}!",
                                    "orange"
                                    )
                                log(video_source,
                                    "orange"
                                    )
                                self.context.collect(
                                    item_id=lecture,
                                    url=video_source,
                                    filepath=filepath.with_suffix('.mp4'))

                                # Break the loop if a valid video URL
                                # is found.
                                if 'transcriptAvailableTranslationsUrl' in json_meta:
                                    # subtitle URL found
                                    subtitle_url = self.urls.COURSE_BASE_URL.format(resource=
                                                                 json_meta.get(
                                                                     'transcriptAvailableTranslationsUrl')
                                                                 .replace("available_translations", "download")
                                                                 )[1:]
                                    log(f"Subtitle was found for: {filepath}!",
                                        "orange"
                                        )

                                    self.context.collect(item_id="srt" + lecture,
                                                         url=subtitle_url,
                                                         filepath=filepath.with_suffix('.srt'))

