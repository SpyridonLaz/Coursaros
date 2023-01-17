import html
import json
import re
import sys
import time
import traceback
from pathlib import Path
import validators
from bs4 import BeautifulSoup
from Exceptions import EdxRequestError, EdxInvalidCourseError, EdxNotEnrolledError
from Courses.Course import BaseCourse
from Platforms.EdxPlatform import Edx
from Urls.EdxUrls import EdxUrls

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass

class EdxCourse(BaseCourse,  ):

    def __init__(self, context: Edx, slug: str ,title= None ):
        super().__init__(context=context, slug= slug,  )
        self.context = context
        super().course_title = title
        self.urls = context.urls
        self.outline_url = '{}/{}'.format(self.urls.COURSE_OUTLINE_BASE_URL, slug)



        # Collects scraped items and separates them from those already found.
        #self.get_xblocks()

    @BaseCourse.slug.setter
    def slug(self, slug: str):
        self._slug = slug if slug and slug.startswith('course-') else self.slug


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
                    self._slug = part

                    return
        else:
            # If the conditions above are not passed, we will assume that a wrong
            # course_dir URL was passed in.
            raise EdxInvalidCourseError('The provided course URL seems to be invalid.')

        # if course_slug in self.collector.negative_results_id:
        # 	return

    @BaseCourse.course_title.setter
    def course_title(self, blocks):
        for block, block_meta in blocks.items():
            if block_meta.get('type') == 'course' and block_meta.get('display_name') is not None:
                course_dir_name = block_meta.get('display_name')
                super().course_title = self.sanitizer(course_dir_name)

        else:
            self._course_title = 'Unnamed EdxCourse-{slug}'.format(slug = self.slug)
        # if course_slug in self.collector.negative_results_id:
        # 	return





    def get_xblocks(self, ):
        # Construct the course_dir outline URL

        # We make an HTTP GET request to outline URL api
        # and return a json object
        # with xblocks:metadata which
        # will allow us to map the course_dir.

        try:
            outline_resp = self.client.get(self.outline_url, headers=self.urls.headers)
        except ConnectionError as e:
            raise EdxRequestError(e)
        try:
            # course_dir's xblock structure.
            # blocks:metadata as keys:values
            blocks = outline_resp.json()
        except Exception as e:
            print(traceback.format_exc(), e)
            sys.exit(1)
        blocks = blocks.get('course_blocks', None)
        if blocks and blocks.get('blocks', None):
            self.xblocks = blocks.get('blocks')
            self.course_title = self.xblocks

        else:
            # If no blocks are found, we will assume that the user is not authorized
            # to access the course_dir.
            raise EdxNotEnrolledError(
                'No course_dir content was found. Check the availability of the course_dir and try again.')

    def build_dir_tree(self):
        self.get_xblocks()
        self.lectures = {k: v for k, v in self.xblocks.items() if v['type'] == 'sequential'}
        self.chapters = {k: v for k, v in self.xblocks.items() if v['type'] == 'chapter' and v['children'] is not None}



        for i, (lecture, lecture_meta) in enumerate(self.lectures.items()):
            lecture_name = re.sub(r'[^\w_ ]', '-', lecture_meta.get('display_name')).replace('/', '-')
            for chapter, chapter_meta in self.chapters.items():
                if lecture in chapter_meta.get('children'):
                    chapter_name = re.sub(r'[^\w_ ]', '-', chapter_meta.get('display_name')).replace('/', '-').strip()
                    chapter_dir = Path.joinpath(self.course_dir, chapter_name)
                    if not Path(chapter_dir).exists():
                        # create lecture Directories
                        Path(chapter_dir).mkdir(parents=True, exist_ok=True)
                        print(f"Creating folder: {chapter_dir}..")
                        print("..ok")
                    lecture_meta.update({'chapter': chapter_name})
                    lecture_meta.update({'chapterID': chapter_meta.get('id')})
                    lecture_meta.update({'course_dir': self.course_dir})
                    # lecture_meta.update({'directory': chapter_dir})

                    filepath = Path(chapter_dir, '{segment} - ' + lecture_name)
                    lecture_meta.update({'filepath': Path.joinpath(chapter_dir, filepath)})

            # assuming that lectures are ordered .

    def main_iterator(self, lectures, ):
        # //TODO  mallon me class poy tha apofasizei poio tha anoiksei ap ta 2(constructor)
        # mallon sto platform
        for i, (lecture, lecture_meta) in enumerate(lectures.items()):
            lecture_url = "{}/{}".format(self.urls.XBLOCK_BASE_URL, lecture)

            soup = None
            for j in range(3):
                try:
                    res = self.client.get(lecture_url,
                                          headers=self.urls.headers,
                                          allow_redirects=True)
                    soup = BeautifulSoup(html.unescape(res.text), 'lxml')
                except Exception as e:
                    if j == 2:
                        raise EdxRequestError(e)
                    time.sleep(5)
                    print("RETRYING")
                    self.context.load_cookies()
                    continue
                else:
                    break

            try:
                # KalturaScraper.KalturaScraper(lecture_meta, slug, soup)

                DefaultEdxScraper(lecture, lecture_meta, self.slug, soup)
            except (KeyboardInterrupt, ConnectionError):
                self.collector.save_results()

            # //TODO  με pandas και με DINJECTION
            self.collector.negative_results_id.add(lecture)
        else:
            self.collector.negative_results_id.add(self.slug)


class DefaultEdxScraper(EdxCourse):

    def scrape(self, lecture, lecture_meta, soup):
        '''
        # Searches through HTML elements
        # Finds and builds URLs for subtitles and videos
        '''
        log("Entered Default")

        for i in soup.find_all('div', {'class': 'xblock-student_view-video'}):

            header_block = i.find('h3', attrs={'class': 'hd hd-2'})
            if header_block:
                segment = re.sub(r'[^\w_ ]', '-', header_block.text).replace('/', '-')
                filepath = lecture_meta.get('filepath').format(segment=segment)

                paragraphs = i.find_all('p')
                if paragraphs and not Path(filepath).with_suffix('.pdf').exists():
                    inner_html = i.decode_contents().replace('src="',
                                                             f'src="{self.urls.PROTOCOL_URL}/')
                    inner_html = inner_html.replace(f'src="{self.urls.PROTOCOL_URL}/http', 'src="http')
                    try:
                        self.collector.save_as_pdf(content=inner_html, path=filepath,
                                                   id=lecture
                                                   )
                        log("PDF saved!", "orange")
                    except Exception as e:
                        print("Problem while building PDF.")
                        print(e)

                meta_block = i.find('div', {'class': 'video', 'data-metadata': True})

                if meta_block:

                    json_meta = json.loads(meta_block.get('data-metadata'))
                    # Get the data-metadata attribute HTML
                    # and parse it as a JSON object.
                    prepared_item = {}
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
                                prepared_item.update(course_slug=self.slug,
                                                     course=lecture_meta.get('course_dir'),
                                                     chapter=lecture_meta.get('chapter'),
                                                     lecture=lecture_meta.get('display_name'),
                                                     id=lecture,
                                                     segment=segment,
                                                     video_url=video_source,
                                                     filepath=filepath)

                                # Break the loop if a valid video URL
                                # is found.
                                subtitle_url = ''
                                if 'transcriptAvailableTranslationsUrl' in json_meta:
                                    # subtitle URL found
                                    subtitle_url = '{}{}'.format(self.urls.PROTOCOL_URL,
                                                                 json_meta.get(
                                                                     'transcriptAvailableTranslationsUrl')
                                                                 .replace("available_translations", "download")
                                                                 )
                                    log(f"Subtitle was found for: {filepath}!",
                                        "orange"
                                        )
                                prepared_item.update(subtitle_url=subtitle_url)

                                self.collector.collect(**prepared_item)
        return
