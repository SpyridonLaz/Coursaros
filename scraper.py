import ast
import html
import json
import os
import pickle
import re
import sys
import time
import traceback
from pathlib import Path

import pdfkit
import requests
import validators
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
from selenium_impl.kaltura import KalturaScraper as ks
from Exceptions import *
from EdxUrls import BaseEdxUrls as edx
try:
    from debug import *

    d = Debugger()
    log = LogMessage()

except ImportError:
    d = print
    pass


#
# Override colorful palette

class EdxDownloader:

    # Create a request session to send cookies
    # automatically for HTTP requests.
    client = requests.session()
    # Cookie location
    # These headers are required. Some may not be required
    # but sending all is a good practice.
    _edx_headers = {
        'Host': edx.EDX_HOSTNAME,
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': None,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': edx.BASE_URL,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': edx.LOGIN_URL,
        'accept-language': 'en-US,en;q=0.9',
    }

    # This is set True later and is used to
    # avoid unnecessary login attempts
    is_authenticated = False

    def __init__(self, email, password,  ):

        self.client = requests.Session()
        # The EDX account's email
        self.edx_email = email
        self.collector = Collector()
        # The EDX account's password
        self.edx_password = password

        self.session_file_exists = Path(edx.SAVED_SESSION_PATH).exists()



    def edx_headers(self):
        # Generate a fake user-agent to avoid 403 error
        self._edx_headers['user-agent'] = UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome
        return self._edx_headers


    def load(self, ):
        if self.session_file_exists and Path(edx.SAVED_SESSION_PATH).stat().st_size > 100:
            with open(edx.SAVED_SESSION_PATH, 'rb') as f:
                self.client = pickle.load(f)
            return True
        else:
            log("pickleJar is empty", "red")
            return False

    def dump(self, ):
        with open(edx.SAVED_SESSION_PATH, 'wb') as f:
            pickle.dump(self.client, f)

    def log_message(self, message, color='blue'):
        # Outputs a colorful message to the terminal
        # and only if 'is_debug' prop is set to True.

            if color == 'blue':
                message = cf.bold & cf.blue | message
            elif color == 'orange':
                message = cf.bold & cf.orange | message
            elif color == 'green':
                message = cf.bold & cf.green | message
            elif color == 'red':
                message = cf.bold & cf.red | message
            print(message)


    def _retrieve_csrf_token(self):
        # Retrieve the CSRF token first
        try:
            self.client.get(edx.LOGIN_URL, timeout=20)  # sets cookie

            if 'csrftoken' in self.client.cookies:
                # Django 1.6 and up
                csrftoken = self.client.cookies.get('csrftoken',None)
                print(csrftoken)
            else:
                # older versions
                csrftoken = self.client.cookies.get('csrf',None)

        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")

        self._edx_headers['x-csrftoken'] = csrftoken



    def sign_in(self):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        self._retrieve_csrf_token()
        data = {
            'email': self.edx_email,
            'password': self.edx_password
        }
        try:
            res = self.client.post(edx.LOGIN_API_URL, headers=self._get_headers(), data=data, timeout=10).json()
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        if res.get('success') is True:
            self.is_authenticated = True
            return True
        else:
            raise EdxLoginError("Login Failed")



    def dashboard_urls(self):
        '''
        The main function to scrape the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired, not enrolled or
        unavailable for any reason.

        returns: A list with the URLs of all available courses.
        '''

        available_courses = []
        try:
            response = self.client.get(edx.DASHBOARD_URL)
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        soup = BeautifulSoup(html.unescape(response.text), 'lxml')
        soup_elem = soup.find_all('a', {'class': 'course-target-link enter-course'})
        if soup_elem:
            for i, element in enumerate(soup_elem):
                course_slug = element.get('data-course-key')

                course_title = soup.find('h3', {'class': 'course-title',
                                                'id': 'course-title-' + course_slug}
                                         )
                print(course_title)
                course_title = course_title.text.strip()

                course_url = "{}/{}/".format(edx.COURSE_BASE_URL, course_slug)
                available_courses.append({'course_title': course_title,
                                          'course_url': course_url,
                                          'course_slug': course_slug}
                                         )
                available_courses.append(course_url) if validators.url(course_url) else None
        print(available_courses)
        self.available_courses = available_courses
        return self.available_courses


class Course:

    def __init__(self,context:EdxDownloader,slug :str=None  ):

        self._client = context.client
        self._collector = context.collector
        self.headers= context.edx_headers()

        self._slug= slug
        self._course_title = slug
        self.get_xblocks()

    @property
    def client(self):
        return self._client
    @property
    def collector(self):
        return self._collector
    @property
    def url(self):
        return self.url

    @property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, slug:str):
        self._slug = slug if slug and slug.startswith('course-') else self.slug

    @url.setter
    def url(self,url):
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
            self._course_title ='Unnamed Course'


    def get_xblocks(self, ):
        # Construct the course outline URL

        self.COURSE_OUTLINE_URL = '{}/{}'.format(edx.COURSE_OUTLINE_BASE_URL, self.slug)
        # We make an HTTP GET request to outline URL api
        # and return a json object
        # with xblocks:metadata which
        # will allow us to map the course.

        try:
            outline_resp = self.client.get(self.COURSE_OUTLINE_URL,  headers=self.headers)
        except ConnectionError as e:
            raise EdxRequestError(e)
        try:
            # course's xblock structure.
            # blocks:metadata as keys:values
            blocks = outline_resp.json()
        except Exception as e:
            print(traceback.format_exc(),e)
            sys.exit(1)
        blocks = blocks.get('course_blocks',None)
        if blocks and blocks.get('blocks',None)  :
            self.xblocks = blocks.get('blocks')
            self.course_title=self.xblocks
        else:
            # If no blocks are found, we will assume that the user is not authorized
            # to access the course.
            raise EdxNotEnrolledError(
                'No course content was found. Check the availability of the course and try again.')




    def course_dir_tree(self):

        lectures = {k: v for k, v in self.xblocks.items() if v['type'] == 'sequential'}
        chapters = {k: v for k, v in self.xblocks.items() if v['type'] == 'chapter' and v['children'] is not None}

        # course directory
        course_name = re.sub(r'[^\w_ ]', '-', self.course_title).replace('/', '-').strip()
        main_course_dir = 'edx'
        main_course_dir = Path.joinpath(Path().home(), main_course_dir, course_name)
        if not Path(main_course_dir).exists():
            # create course Directory
            Path(main_course_dir).mkdir(parents=True, exist_ok=True)

        for i, (lecture, lecture_meta) in enumerate(lectures.items()):
            lecture_name = re.sub(r'[^\w_ ]', '-', lecture_meta.get('display_name')).replace('/', '-')
            for chapter, chapter_meta in chapters.items():
                if lecture in chapter_meta.get('children'):
                    chapter_name = re.sub(r'[^\w_ ]', '-', chapter_meta.get('display_name')).replace('/', '-').strip()
                    chapter_dir = Path.joinpath(main_course_dir, chapter_name)
                    if not Path(chapter_dir).exists():
                        # create lecture Directories
                        Path(chapter_dir).mkdir(parents=True, exist_ok=True)
                        print(f"Creating folder: {chapter_dir}..")
                        print("..ok")
                    lecture_meta.update({'chapter': chapter_name})
                    lecture_meta.update({'chapterID': chapter_meta.get('id')})
                    lecture_meta.update({'course': self.course_title})
                    # //TODO  να καταργησω το διρεψτορυ + ναμε. να το κανω ολοκληρο

                    lecture_meta.update({'directory': chapter_dir})

                    filename = Path(chapter_dir,'{segment} - ' + f'{lecture_name}')
                    lecture_meta.update({'filename': Path.joinpath(chapter_dir, filename)})

            # assuming that lectures are ordered .



    def main_iterator(self,lectures,):
        #//TODO  mallon me class poy tha apofasizei poio tha anoiksei ap ta 2(constructor)

        for i, (lecture, lecture_meta) in enumerate(lectures.items()):

            lecture_url = "{}/{}".format(edx._XBLOCK_BASE_URL, lecture)

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

                    DefaultScraper(self,lecture, lecture_meta, self.slug, soup)
            except (KeyboardInterrupt, ConnectionError):
                self.collector.save_results()


        #//TODO  με pandas και με DINJECTION
            self.collector.negative_results_id.add(lecture)
        else:
            self.collector.negative_results_id.add(self.slug)



class DefaultScraper(Course):
    def __init__(self, context: EdxDownloader,lecture, lecture_meta, slug, soup):
        super().__init__(context)
        self.soup = soup
        self.slug = slug
        self.lecture_meta = lecture_meta
        self.lecture = lecture

    def scrape(self, lecture, lecture_meta, soup):
        '''
        # Searches through HTML elements
        # Finds and builds URLs for subtitles and videos
        '''
        log("Entered Default")

        directory = lecture_meta.get('directory')

        for i in soup.find_all('div', {'class': 'xblock-student_view-video'}):

            header_block = i.find('h3', attrs={'class': 'hd hd-2'})
            if header_block:
                segment_title = re.sub(r'[^\w_ ]', '-', header_block.text).replace('/', '-')
                filename = lecture_meta.get('filename').format(segment=segment_title)
                total_file_path = Path.joinpath(directory, filename)

                paragraphs = i.find_all('p')
                #//TODO  να καταργησω το διρεψτορυ + ναμε. να το κανω ολοκληρο
                if paragraphs and not Path(total_file_path + '.pdf').exists():
                    inner_html = i.decode_contents().replace('src="',
                                                             f'src="{edx.BASE_URL}/')
                    inner_html = inner_html.replace(f'src="{edx.BASE_URL}/http', 'src="http')
                    try:
                        self.collector.save_as_pdf(inner_html, total_file_path,
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
                                log(f"Struck gold! A video was found in segment: {filename}!",
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
                                                     segment=segment_title,
                                                     directory=directory,
                                                     video_url=video_source,
                                                     filename=filename)

                                # Break the loop if a valid video URL
                                # is found.
                                subtitle_url = ''
                                if 'transcriptAvailableTranslationsUrl' in json_meta:
                                    # subtitle URL found
                                    subtitle_url = '{}{}'.format(edx.BASE_URL,
                                                                 json_meta.get(
                                                                     'transcriptAvailableTranslationsUrl')
                                                                 .replace("available_translations", "download")
                                                                 )
                                    log(f"Subtitle was found for: {filename}!",
                                        "orange"
                                        )
                                prepared_item.update(subtitle_url=subtitle_url)

                                self.collector(**prepared_item)
        return


class Collector:
    # todo olo
    all_videos = []

    # ID's of previously found positive results.
    positive_results_id = set()

    # ID's of previously found negative results.
    negative_results_id = set()

    pdf_results_id = set()
    def __init__(self):
        """
		Collects dict items that will be sent to the downloader later.
		Saves result in designated folders.
		Saves negative results.
		Saves result where a pdf file was created.
		"""

        # list of positive dictionary item objects that will be RETURNED to main()
        # for download

        self.pdf_results = edx.BASE_FILEPATH.as_uri().format(file='.edxPDFResults')

        self.results = edx.BASE_FILEPATH.as_uri().format(file='.edxResults')
        self.negative_results = edx.BASE_FILEPATH.as_uri().format(file='.edxResults_bad')

        with open(self.results, "r") as f:
            # reads previously found positive results .
            for line in f:
                d = ast.literal_eval(line)
                if not d.get('id') in self.positive_results_id:
                    # loading previous dict results
                    self.all_videos.append(d)
                    # collecting ids in set() to avoid duplicates
                    self.positive_results_id.add(d.get('id'))

        with open(self.negative_results) as f:
            # loads previously found negative pages where no video was found.
            self.negative_results_id = set(line.strip() for line in f)

        if True:
            with open(self.pdf_results) as f:
                # loads previously found negative pages where no  was found.
                self.pdf_results_id = set(line.strip() for line in f)

    def __iter__(self):
        return [x for x in self.all_videos]

    def __call__(self, id, course, course_slug, chapter, lecture, segment,
                 video_url, filename, directory, subtitle_url=''):
        '''
            param id: id of current block where item was found
            param course: name of Course,
            param course_slug: slug of course
            param chapter: current chapter
            param lecture: lecture (sequence)
            param segment: Segment or video name
            param video_url:  video url
            param filename: base filename, without suffix
            param directory: directory of file
            param subtitle_url:  subtitle url
            return: bool
		'''

        item = locals()
        item.pop('self')
        if item.get('id') not in self.positive_results_id:
            # avoids duplicates
            if not validators.url(item.get('subtitle_url')):
                item.pop('subtitle_url')

            self.all_videos.append(item)
            self.positive_results_id.add(item.get('id'))
            print(len(self.all_videos))
            return True
        else:
            return False



    def save_results(self, ):
        '''
		:return:list(dict()) self.all_videos
		Saves all results in file to later reuse.
		'''
        with DelayedKeyboardInterrupt() :
            with open(self.results, 'w') as f:
                for result in self.all_videos:
                    f.write(str(result) + '\n')

            with open(self.negative_results, "w") as f:
                for negative_id in self.negative_results_id:
                    f.write(str(negative_id) + '\n')

            if True:
                with open(self.pdf_results, "w") as f:
                    for pdf_id in self.pdf_results_id:
                        f.write(str(pdf_id) + '\n')

            print("SEARCH RESULTS SAVED IN ~/.edxResults")

    def save_as_pdf(self, string: str, path: str, id: str):
        '''
        :param string: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        pdf_save_as = f'{path}.pdf'
        pdfkit.from_string(string, output_path=pdf_save_as)
        self.pdf_results_id.add(id)


class Downloader():
    # TODO OLO
    # Chunk size to download videos in chunks
    VID_CHUNK_SIZE = 1024
    def __init__(self, client: requests.Session, url: str, save_as: str, desc: str):

            self.client = client
            self.url = url
            self.save_as = save_as
            self.desc = desc
            self.headers = {'x-csrftoken': self.client.cookies.get_dict().get('csrftoken')}

    @staticmethod
    def file_exists(func):
        def inner(self):
            if Path(self.save_as).exists():
                # if file exists
                log(f'Already downloaded. Skipping: {self.desc}.{self.save_as.split(".")[-1:]}')
                return False
            func(self)
        return inner



    def change_user_state(self, ):
        '''
		# Subtitles are either downloaded as (.srt) or as transcripts (.txt)
		# depending on  "user_state"  that is saved server side and we cannot
		# make the choice with a simple GET request.
		# Thus, a POST request is required , which will change the user state
		# to the following  "transcript_download_format": "srt".
		'''
        def inner(self):
            for i in range(4):
                try:
                    save_user_state = self.url.replace("transcript", "xmodule_handler").replace("download",
                                                                                                "save_user_state")
                    payload = {"transcript_download_format": "srt"}

                    post_response = self.client.post(url=save_user_state,
                                                     cookies=self.client.cookies.get_dict(),
                                                     headers=self.headers,
                                                     data=payload
                                                     )
                except ConnectionError as e:
                    if i == 1:
                        raise EdxRequestError(e)
                    continue

                else:
                    if post_response.status_code == 200:
                        break
                    else:
                        continue
            else:
                return False

    @file_exists
    def download(self, ):
        #todo to pame sto scraper
        # s = 'srt' if self.save_as else 'mp4'
        log('Downloading: {name}'.format(name=self.desc,))
        # temporary name to avoid duplication.
        save_as_parted = f"{self.save_as}.part"
        # In order to make downloader resumable, we need to set our headers with
        # a correct Range value. we need the bytesize of our incomplete file and
        # the content-length from the file's header.

        current_size_file = os.path.getsize(save_as_parted) if os.path.exists(save_as_parted) else 0
        range_headers = {'Range': f'bytes={current_size_file}-'}

        # print("url", url)
        # HEAD response will reveal length and url(if redirected).
        head_response = self.client.head(self.url,
                                         headers=self.headers.update(range_headers),
                                         allow_redirects=True,
                                         timeout=60)

        url = head_response.url
        # file_size str-->int (remember we need to build bytesize range)
        file_size = int(head_response.headers.get('Content-Length', 0))

        progress_bar = tqdm(initial=current_size_file,
                            total=file_size,
                            unit='B',
                            unit_scale=True,
                            smoothing=0,
                            desc=f'{self.desc}',
                            file=sys.stdout,
                            )
        # We set the progress bar to the size of already
        # downloaded .part file
        # to display the correct length.
        with self.client.get(url,
                             headers=range_headers,
                             stream=True,
                             allow_redirects=True,
                             ) as resp:

            with open(save_as_parted, 'ab') as f:
                for chunk in resp.iter_content(chunk_size=self.VID_CHUNK_SIZE * 100):
                    # -write response data chunks to file_size
                    # - Updates progress_bar
                    progress_bar.update(len(chunk))
                    f.write(chunk)

        progress_bar.close()
        if file_size == os.path.getsize(save_as_parted):
            # assuming downloaded file has correct number of bytes(size)
            # then we rename with correct suffix.
            os.rename(save_as_parted, self.save_as)
            return True
        elif file_size < os.path.getsize(save_as_parted):
            # deletes file if downloaded bytes are more
            # than those declared by server.
            os.remove(save_as_parted)
            return False
        else:
            print("unknown error")
            return False

class KalturaDownloader(Downloader):
    def __init__(self, client: requests.Session, url: str, save_as: str, desc: str,):

        super().__init__(client, url, save_as , desc)

        self.download = self._change_user_state(self.download) if Path(self.save_as) else self.download


    @staticmethod
    def _change_user_state(func, ):
        '''
        # Subtitles are either downloaded as (.srt) or as transcripts (.txt)
        # depending on  "user_state"  that is saved serverside, and we cannot
        # make the choice with a simple GET request.
        # Thus, a POST request is required , which will change the user state
        # to the following  "transcript_download_format": "srt".
        '''
        def inner (self):
            for i in range(4):
                try:
                    save_user_state = self.url.replace("transcript", "xmodule_handler").replace("download",
                                                                                                "save_user_state")
                    payload = {"transcript_download_format": "srt"}

                    response = self.client.post(url=save_user_state,
                                                cookies=self.client.cookies.get_dict(),
                                                headers=self.headers,
                                                data=payload
                                                )
                except ConnectionError as e:
                    time.sleep(1)
                    if i == 3:
                        raise EdxRequestError(e)
                    continue

                else:
                    if response.status_code == 200:
                        return inner(func)
                    else:
                        continue
            else:
                return func

