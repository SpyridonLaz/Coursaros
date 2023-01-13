
from Course.Course import Course
from Platform.EdxPlatform import *



class EdxCourse(Course):

    def __init__(self, context: Edx, slug: str = None, *args, ):
        super().__init__(context, slug, *args)
        self.get_xblocks()
        self.COURSE_OUTLINE_URL = '{}/{}'.format(self.COURSE_OUTLINE_BASE_URL, slug)

    @Course.slug.setter
    def slug(self, slug: str):
        self._slug = slug if slug and slug.startswith('course-') else self.slug

    @Course.url.setter
    def url(self, url):
        '''
         This method expects a course's URL as argument, searches for it's xBlock structure and, if found, it returns it as a dictionary,else raises exception.
        '''

        log('Building xblocks.')
        # TODO  URL CHECK START
        # Break down the given course URL to get the course slug.
        if validators.url(url):
            for part in url.split('/'):
                if part.startswith('course-'):
                    self._slug = part

                    return
        else:
            # If the conditions above are not passed, we will assume that a wrong
            # course URL was passed in.
            raise EdxInvalidCourseError('The provided course URL seems to be invalid.')

        # if course_slug in self.collector.negative_results_id:
        # 	return

    @Course.course_dir.setter
    def course_dir(self, value):
        for block, block_meta in value.items():
            if block_meta.get('type') == 'course' and block_meta.get('display_name') is not None:
                course_dir_name = block_meta.get('display_name')
                dir_name_stripped = re.sub(r'[^\w_ ]', '-', course_dir_name).replace('/', '-').strip()
                self.course_dir = Path.joinpath(self.BASE_FILEPATH, self.platform, dir_name_stripped)
                return
        else:
            self._course_dir = 'Unnamed EdxCourse'
        # if course_slug in self.collector.negative_results_id:
        # 	return

    @property
    def course_title(self):
        return self._course_title

    @course_title.setter
    def course_title(self, value):
        for block, block_meta in value.items():
            if block_meta.get('type') == 'course' and block_meta.get('display_name') is not None:
                self._course_title = block_meta.get('display_name')
                return

        else:
            self._course_title = 'Unnamed EdxCourse'

    def get_xblocks(self, ):
        # Construct the course outline URL

        # We make an HTTP GET request to outline URL api
        # and return a json object
        # with xblocks:metadata which
        # will allow us to map the course.

        try:
            outline_resp = self.client.get(self.COURSE_OUTLINE_URL, headers=self.headers)
        except ConnectionError as e:
            raise EdxRequestError(e)
        try:
            # course's xblock structure.
            # blocks:metadata as keys:values
            blocks = outline_resp.json()
        except Exception as e:
            print(traceback.format_exc(), e)
            sys.exit(1)
        blocks = blocks.get('course_blocks', None)
        if blocks and blocks.get('blocks', None):
            self.xblocks = blocks.get('blocks')
            self.course_dir = self.course_dir()
        else:
            # If no blocks are found, we will assume that the user is not authorized
            # to access the course.
            raise EdxNotEnrolledError(
                'No course content was found. Check the availability of the course and try again.')

    def build_dir_tree(self):

        self.lectures = {k: v for k, v in self.xblocks.items() if v['type'] == 'sequential'}
        self.chapters = {k: v for k, v in self.xblocks.items() if v['type'] == 'chapter' and v['children'] is not None}

        # course directory

        if not Path(self.course_dir).exists():
            # create course Directory
            Path(self.course_dir).mkdir(parents=True, exist_ok=True)

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
                    lecture_meta.update({'course': self.course_dir})
                    # lecture_meta.update({'directory': chapter_dir})

                    filepath = Path(chapter_dir, '{segment} - ' + lecture_name)
                    lecture_meta.update({'filepath': Path.joinpath(chapter_dir, filepath)})

            # assuming that lectures are ordered .

    def main_iterator(self, lectures, ):
        # //TODO  mallon me class poy tha apofasizei poio tha anoiksei ap ta 2(constructor)

        for i, (lecture, lecture_meta) in enumerate(lectures.items()):

            lecture_url = "{}/{}".format(self.XBLOCK_BASE_URL, lecture)

            soup = None
            for j in range(3):
                try:
                    res = self.client.get(lecture_url,
                                          headers=self.headers,
                                          allow_redirects=True)
                    soup = BeautifulSoup(html.unescape(res.text), 'lxml')
                except Exception as e:
                    if j == 2:
                        raise EdxRequestError(e)
                    time.sleep(5)
                    print("RETRYING")
                    self.load()
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
                                                             f'src="{self.PROTOCOL_URL}/')
                    inner_html = inner_html.replace(f'src="{self.PROTOCOL_URL}/http', 'src="http')
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
                                                     course=lecture_meta.get('course'),
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
                                    subtitle_url = '{}{}'.format(self.PROTOCOL_URL,
                                                                 json_meta.get(
                                                                     'transcriptAvailableTranslationsUrl')
                                                                 .replace("available_translations", "download")
                                                                 )
                                    log(f"Subtitle was found for: {filepath}!",
                                        "orange"
                                        )
                                prepared_item.update(subtitle_url=subtitle_url)

                                self.collector(**prepared_item)
        return
