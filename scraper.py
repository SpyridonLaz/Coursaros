import requests
from bs4 import BeautifulSoup
import html
from fake_useragent import UserAgent
import colorful as cf
from tqdm import tqdm

import time
from  Exceptions import *

try:
    from  debug import debugger
    #this is basically a print with a counter
    d = debugger()
except ImportError:
    d = print
    pass

# Override colorful palette
ci_colors = {
    'green': '#42ba96',
    'orange': '#ffc107',
    'red': '#df4759',
    'blue': '#5dade2'
}

cf.update_palette(ci_colors)



class EdxDownloader:
    # Base URLs as pseudo constants
    EDX_HOSTNAME = 'courses.edx.org'
    BASE_URL = 'https://{}'.format(EDX_HOSTNAME)
    LMS_BASE_URL = 'https://learning.edx.org'
    BASE_API_URL = '{}/api'.format(BASE_URL)
    LOGIN_URL = '{}/login'.format(BASE_URL)
    COURSE_BASE_URL = '{}/courses'.format(BASE_URL)
    COURSE_OUTLINE_BASE_URL = '{}/course_home/v1/outline'.format(BASE_API_URL)
    XBLOCK_BASE_URL = '{}/xblock'.format(BASE_URL)
    LOGIN_API_URL = '{}/user/v1/account/login_session/'.format(BASE_API_URL)
    DASHBOARD_URL = '{}/dashboard/'.format(BASE_URL)

    # Chunk size to download videos in chunks
    VID_CHUNK_SIZE = 1024

    # Create a request session to send cookies
    # automatically for HTTP requests.
    client = requests.session()
    # Generate a fake user-agent to avoid blocks
    user_agent  = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')
    # These headers are required. Some may not be required
    # but sending all is a good practice.
    edx_headers = {
        'Host': EDX_HOSTNAME,
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': user_agent.chrome,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': BASE_URL,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': LOGIN_URL,
        'accept-language': 'en-US,en;q=0.9',
    }



    def __init__(self, email, password, is_debug=True, is_colored=False):
        # This is set True later and is used to
        # avoid unnecessary login attempts
        self.is_authenticated = False

        # When it is set False, the log_message()
        # function will not print anything.
        self.is_debug = is_debug

        # When this is set to True the log_message()
        # function will print in color.
        self.is_colored = is_colored

        # The EDX account's email
        self.edx_email = email

        # The EDX account's password
        self.edx_password = password

    def log_message(self, message, color='blue'):
        # Outputs a colorful message to the terminal
        # and only if 'is_debug' prop is set to True.

        if self.is_debug:
            if self.is_colored:
                if color == 'blue':
                    message = cf.bold & cf.blue | message
                elif color == 'orange':
                    message = cf.bold & cf.orange | message
                elif color == 'green':
                    message = cf.bold & cf.green | message
                elif color == 'red':
                    message = cf.bold & cf.red | message
                print(message)
            else:
                print(message)
        # if self.is_debug:
        #     if color == 'blue':
        #         message = cf.bold | cf.blue(message)
        #     elif color == 'orange':
        #         message = cf.bold | cf.orange(message)
        #     elif color == 'green':
        #         message = cf.bold | cf.green(message)
        #     elif color == 'red':
        #         message = cf.bold | cf.red(message)
        #     print(message)

    def sign_in(self):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        # html_res = self.requests_session.get(LOGIN_URL)
        # Retrieve the CSRF token first
        try:
            self.client.get(self.LOGIN_URL, timeout=20)  # sets cookie
            if 'csrftoken' in self.client.cookies:
                # Django 1.6 and up
                csrftoken = self.client.cookies['csrftoken']
                print(csrftoken)
            else:
                # older versions
                csrftoken = self.client.cookies['csrf']
            self.edx_headers['x-csrftoken'] = csrftoken
            data = {
                'email': self.edx_email,
                'password': self.edx_password
            }
            res = self.client.post(self.LOGIN_API_URL, headers=self.edx_headers, data=data, timeout=10).json()

            if res.get('success') is True:
                self.is_authenticated = True
                return True
            else:
                if res.get("value"):
                    raise EdxLoginError(res.get('value'))
        except ConnectionError as e:
            raise EdxRequestError("Connection or CSRF token problem")

    def experimental_scrape(self, soup):
        d("---inside experimental---")
        '''
        # we run a second client GET request by using
        # the parent's <iframe src="{nested iframe URL}"
        # attribute to dwelve deeper into it's nested content which will
        # eventually include both the video URL and subtitles URL.
        '''
        parent_iframe = soup.find('iframe', {'id': 'kaltura_player'})

        if parent_iframe:
            # GET request and bs4 the nested response
            nested_res = self.client.get(parent_iframe['src'])
            d("iframe found from source")
            time.sleep(5)
            nested_soup = BeautifulSoup(html.unescape(nested_res.text), 'lxml')

            d(f'NESTED SOUP {nested_soup}')
            # TODO  ####################################################################

            # METHOD 1 WITH CREATING DICTIONARY
            video_tag_list = nested_soup.find_all('video', attrs={'id': ['pid_kaltura_player', 'kaltura_player']})
            subtitles = nested_soup.find_all('track')

            d(f"Number of subtitles found :{len(subtitles)} {subtitles}")

            if video_tag_list and len(video_tag_list) == 1:
                video_tag = video_tag_list[0]
                # print("debugger:-LIST OF Video elements :", nested_all_data)
                if video_tag:
                    tagId = video_tag['id']
                    partnerId = video_tag['kpartnerid']
                    entryId = video_tag['kentryid']
                    d(f"tagID:<video id=\"{tagId}\"> | partnerid: {partnerId} | entryId: {entryId}")

                    # base URL from official kaltura.com API documentation
                    base_URL = "https://cdnapisec.kaltura.com/p/{PID}/sp/{PID}00/playManifest/entryId/{entryId}/format/download/protocol/https/flavorParamIds/0"
                    downloadUrl = base_URL.format(PID=partnerId, entryId=entryId)
                    print(downloadUrl)
                    return downloadUrl

                # #TODO METHOD 2 WITH STRING SPLIT [semi-working]  START
                # # DO NOT DELETE
                # nested_data = nested_soup.find_all('script',{'type':'text/javascript'})
                # #d("debugger:-script-javascript", nested_data)
                # script_list = []
                #
                # for script in nested_data:
                #
                #     texted = script.text
                #     if "downloadUrl" in texted :
                #         texted = texted[texted.find('{'):texted.rfind('}')+1]
                #         try:
                #             info_as_dict = json.loads(texted)
                #             downloadUrl = info_as_dict['entryResult']['meta']['downloadUrl']
                #             d(downloadUrl)
                #             return
                #         except Exception:
                #             print (traceback.format_exc())
                # #TODO END [semi-working]
                # # DO NOT DELETE

        return True

    def dashboard_urls(self):
        '''
        The following function scrapes the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired.

        '''
        available_courses = []
        request = None
        try:
            request = self.client.get(self.DASHBOARD_URL)
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        soup = BeautifulSoup(html.unescape(request.text), 'lxml')
        soup_elem = soup.find_all('a', {'class': 'course-target-link enter-course'})
        if soup_elem:
            for i in soup_elem:
                COURSE_SLUG = i['data-course-key']
                build = "{}/{}/".format(self.BASE_URL, COURSE_SLUG)
                available_courses.append(build)
        print(available_courses)
        return available_courses

    def get_course_data(self, course_url=None):
        # Gets the course media URLs. The media URLs are returned
        # as a list if found.
        # todo
        # data = self.dashboard_urls()

        # TODO  ( IS URL A VALID COURSE ? ) START
        # Break down the course URL to get course slug.
        url_parts = course_url.split('/')
        if len(url_parts) >= 4 and url_parts[4].startswith('course-'):
            COURSE_SLUG = url_parts[4]
        else:
            # If the conditions above are not passed, we will assume that a wrong
            # course URL was passed in.
            raise EdxInvalidCourseError('The provided course URL seems to be invalid.')
        # Construct the course outline URL
        COURSE_OUTLINE_URL = '{}/{}'.format(self.COURSE_OUTLINE_BASE_URL, COURSE_SLUG)
        # TODO  ( IS URL A VALID COURSE ? ) END

        # TODO is_authenticated start
        # Check either authenticated or not before proceeding.
        # If not, raise the EdxNotAuthenticatedError exception.
        if not self.is_authenticated:
            raise EdxNotAuthenticatedError('Course data cannot be retrieved without getting authenticated.')
        # todo is_authenticated end

        # TODO Mapper START

        # Make an HTTP GET request to outline URL and return dictionary object
        # with blocks:metadata as keys:values which will help us iterate the course.

        # TODO ConnectionManager START
        try:
            outline_resp = self.client.get(COURSE_OUTLINE_URL, timeout=20)
        except ConnectionError as e:
            raise EdxRequestError(e)
        # TODO ConnectionManager STOP
        # Transforms response into dict and returns the course's block structure into variable 'blocks'.
        # blocks:metadata as keys:values
        blocks = outline_resp.json()
        if blocks is None:
            # If no blocks are found, we will assume that the user is not authorized
            # to access the course.
            raise EdxNotEnrolledError('No course content was found. Check your enrollment status and try again.')
        else:
            blocks = blocks.get('course_blocks').get('blocks')

        # collection of video download URLs
        collected_vids = []
        #  list of dicts objects
        all_videos = []

        # Iterate through blocks and retrieve course name, video URLs, and video titles.
        courseMap = None
        chapter = None
        chapter_children = {}

        lecture_segment = None
        video_url = None
        course_title = None

        for block, block_meta in blocks.items():
            if block_meta.get('type') == 'course' and block_meta.get('display_name') is not None:
                # course_title = block_meta.get('children')
                course_title = block_meta.get('display_name')
            if block_meta.get('type') == 'chapter' and block_meta.get('children') is not None:
                for child in block_meta.get('children'):
                    chapter_children.update((child, {block_meta.get('type'): block_meta.get('display_name')}))

        print('children', chapter_children)

        lectures = {k: v for k, v in blocks.items() if v['type'] == 'sequential'}
        chapters = {k: v['children'] for k, v in blocks.items() if v['type'] == 'chapter' and v['children']}
        #
        # for chapter,metadata in chapters.items() :
        #     for child in metadata.get('children'):
        #         if child is not None:
        #
        #             s = lectures[child].update(dict({'chapter':chapter}))
        #             print (s)

        for lecture, metadata in lectures.items():

            for chapter, chapter_metadata in chapters.items():
                if metadata.get('id') in chapter_metadata.get('children'):
                    chapter_children.update((lecture, {'chapter': chapter}))

            # lectures are the equivalent of sequentials from course block .
            block_id = metadata.get('id')
            block_url = '{}/{}/jump_to/{}'.format(self.COURSE_BASE_URL, COURSE_SLUG, block_id)
            block_res = self.client.get(block_url)
            main_block_id = block_res.url.split('/')[-1]
            main_block_url = '{}/{}'.format(self.XBLOCK_BASE_URL, main_block_id)
            # TODO Mapper STOP

            d("URL for SCRAPING: ", metadata['display_name'] + "  " + main_block_url)

            # TODO ConnectionManager START
            try:
                main_block_res = self.client.get(main_block_url)
            except ConnectionError as e:
                raise EdxRequestError(e)
            soup = BeautifulSoup(html.unescape(main_block_res.text), 'lxml')
            # TODO ConnectionManager STOP
            d("DEBUG   :SOUP", main_block_res.text)

            # TODO  PageScraper START
            if soup:

                video_url = soup.find('a', attrs={'class': 'btn-link video-sources video-download-button'})

                segment_title = soup.find('button', attrs={'button', 'active btn btn-link'})
                d("DEBUG   :SOUP", soup)
                sub_url = ''
                # video_title = '{} - {}'.format(lecture_title, vid_heading_el.text.strip())

                # Searches through HTML <a> elements
                # Finds and builds URL for subtitles

                if video_url and segment_title:
                    # video URL found
                    video_url = video_url.get('href')
                    segment_title = segment_title.get('title')
                    # Finds and builds URL for subtitles
                    sub_elem = soup.find('a', {'data-value': 'srt'})
                    if sub_elem:
                        sub_url = '{}/{}'.format(self.BASE_URL, sub_elem.get('href'))
                        # subtitle URL found
                    else:
                        pass
                    print(video_url)
                    print(sub_url)

                # Append the video object to all_videos list
                all_videos.append({
                    'course': course_title,  # check
                    'chapter': metadata['chapter'],
                    'lecture': metadata['display_name'],
                    'title': segment_title,
                    'url': video_url,  # check
                    'sub': sub_url  # check
                })
                chapter_children.update({lecture:
                     {'course': course_title,  # check
                      'chapter':  metadata['chapter'],
                      'lecture': metadata['display_name'],
                      'title': segment_title,
                      'video': video_url,  # check
                      'sub': sub_url  # check
                      }}
                                        )
                print(chapter_children)
                collected_vids.append(video_url)
            # TODO  PageScraper STOP

            # TODO dataConstructor START
            # MH DIAGRAFEI
            # TODO dataConstructor STOP

        return all_videos


    def download_video(self, vid_url, save_as):
        print("DOWNLOAD SUCCESS")
        # Download the video
        with self.client.get(vid_url, stream=True) as resp:
            total_size_in_bytes= int(resp.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(save_as, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=self.VID_CHUNK_SIZE):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()
        return True
