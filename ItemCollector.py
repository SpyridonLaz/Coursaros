import sys
import time
from pathlib import Path
import pdfkit
import requests
import validators
import ast
from tqdm import tqdm
from Exceptions import EdxRequestError

try:
    from debug import LogMessage as log, Debugger as d
except ImportError:
    log = print
    d = print
    pass


class Collector:
    """
        Collects dict items that will be sent to the downloader later.
        Saves result in designated folders.
        Saves negative results.
        Saves result where a pdf file was created.
        """
    # TODO REWORK WITH PANDAS
    all_videos = []

    # ID's of previously found positive results.
    positive_results_id = set()

    # ID's of previously found negative results.
    negative_results_id = set()

    pdf_results_id = set()

    def __init__(self, SAVE_TO):
        self.SAVE_TO = SAVE_TO
        self.pdf_results = self.SAVE_TO
        self.positive = self.SAVE_TO
        self.negative = self.SAVE_TO

        # list of positive dictionary item objects that will be RETURNED to main()
        # for download

        with self.positive.open("r") as f :
            # reads previously found positive results .
            for line in f:
                d = ast.literal_eval(line)
                if not d.get('id') in self.positive_results_id:
                    # loading previous dict results
                    self.all_videos.append(d)
                    # collecting ids in set() to avoid duplicates
                    self.positive_results_id.add(d.get('id'))

        with self.negative.open("r") as f:
            # loads previously found negative pages where no video was found.
            self.negative_results_id = set(line.strip() for line in f)

        with self.pdf_results.open("r") as f:
            # loads previously found negative pages where no  was found.
            self.pdf_results_id = set(line.strip() for line in f)

    @property
    def SAVE_TO(self):
        return self._save_as

    @SAVE_TO.setter
    def SAVE_TO(self, path):
        path = Path(path).resolve()
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._save_as = path

    @property
    def pdf_results(self):
        return self._pdf_results

    @pdf_results.setter
    def pdf_results(self, path):
        path = Path(path, '.Results_RDF').resolve()
        path.touch(exist_ok=True)
        self._pdf_results = path

    @property
    def positive(self):
        return self._positive

    @positive.setter
    def positive(self, path):
        path = Path(path, '.Results_Positive').resolve()
        path.touch(exist_ok=True)

        self._positive = path

    @property
    def negative(self):
        return self._negative

    @negative.setter
    def negative(self, path):
        path = Path(path, '.Results_Negative').resolve()
        path.touch(exist_ok=True)

        self._negative = path

    def __iter__(self):
        return [x for x in self.all_videos]

    def collect(self, id, course, course_slug, chapter, lecture, segment,
                 video_url, filepath, ):
        '''
            param id: id of current block where item was found
            param course_dir: name of EdxCourse,
            param course_slug: slug of course_dir
            param chapter: current chapter
            param lecture: lecture (sequence)
            param segment: Segment or video name
            param video_url:  video url
            param filepath: relative filepath
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
        """
            return:list(dict()) self.all_videos
		    Saves all results in file to later reuse.
		"""

        from debug import DelayedKeyboardInterrupt
        with DelayedKeyboardInterrupt():
            with open(self.positive, 'w+') as f:
                for result in self.all_videos:
                    f.write(str(result) + '\n')

            with open(self.negative, "w+") as f:
                for negative_id in self.negative_results_id:
                    f.write(str(negative_id) + '\n')

            with open(self.pdf_results, "w+") as f:
                for pdf_id in self.pdf_results_id:
                    f.write(str(pdf_id) + '\n')

            print("SEARCH RESULTS SAVED IN ~/.edxResults")

    def save_as_pdf(self, content: str, path: str, id: str):
        '''
        :param content: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        pdf_save_as = Path(path)
        pdfkit.from_string(content, output_path=pdf_save_as)
        self.pdf_results_id.add(id)


class Downloadable():
    # Chunk size to download videos in chunks
    VID_CHUNK_SIZE = 1024

    def __init__(self, client: requests.Session, url: str, save_as: str | Path, ):

        self.client = client
        self.url = url
        self.save_as = Path(save_as)
        self.headers = {'x-csrftoken': self.client.cookies.get_dict().get('csrftoken')}

    @staticmethod
    def file_exists(func):
        def inner(self):
            if Path(self.SAVE_TO).exists():
                # if file exists
                log(f'Already downloaded. Skipping: {self.SAVE_TO.name}')
                func()

        return inner

    @file_exists
    def download(self, ):
        # todo to pame sto scraper
        log('Downloading: {name}'.format(name=self.save_as.name, ))
        # temporary name to avoid duplication.
        download_to_part = f"{self.save_as}.part"
        # In order to make downloader resumable, we need to set our headers with
        # a correct Range path. we need the bytesize of our incomplete file and
        # the content-length from the file's header.

        current_size_file = Path(download_to_part).stat() if Path(download_to_part).exists() else 0
        range_headers = {'Range': f'bytes={current_size_file}-'}

        # print("url", url)
        # HEAD response will reveal length and url(if redirected).
        head_response = self.client.head(self.url,
                                         headers=self.headers.update(range_headers),
                                         allow_redirects=True,
                                         timeout=60)

        url = head_response.url
        # file_content_length str-->int (remember we need to build bytesize range)
        file_content_length = head_response.headers.get('Content-Length', 0)

        progress_bar = tqdm(initial=current_size_file,
                            total=int(file_content_length),
                            unit='B',
                            unit_scale=True,
                            smoothing=0,
                            desc=f'{self.save_as.name}',
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

            with open(download_to_part, 'ab') as f:
                for chunk in resp.iter_content(chunk_size=self.VID_CHUNK_SIZE * 100):
                    # -write response data chunks to file_content_length
                    # - Updates progress_bar
                    progress_bar.update(len(chunk))
                    f.write(chunk)

        progress_bar.close()
        if file_content_length == Path(download_to_part).stat():
            # assuming downloaded file has correct number of bytes(size)
            # then we rename with correct suffix.
            Path.rename(download_to_part, self.save_as)
            return True

        else:
            log(f'Incomplete download. Removing: {self.save_as.name}')
            Path(download_to_part).unlink()
            return False



class KalturaDownloadable(Downloadable):
    def __init__(self, client: requests.Session, url: str, save_as: str, ):

        super().__init__(client, url, save_as, )

    @staticmethod
    def _change_user_state(func):
        '''
        # Subtitles are either downloaded as (.srt) or as transcripts (.txt)
        # depending on  "user_state"  that is saved serverside, and we cannot
        # make the choice with a simple GET request.
        # Thus, a POST request is required , which will change the user state
        # to the following  "transcript_download_format": "srt".
        '''

        def inner(self):
            if Path(self.SAVE_TO).suffix == '.srt':

                for i in range(4):
                    try:
                        save_user_state = self.url.replace("transcript", "xmodule_handler").replace("download",
                                                                                                    "save_user_state")
                        payload = {"transcript_download_format": "srt"}

                        response = self.client.post(
                            url=save_user_state, cookies=self.client.cookies.get_dict(),
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
                            func()
                        else:
                            continue

        return inner

    @_change_user_state
    def download(self):
        return super().download()
