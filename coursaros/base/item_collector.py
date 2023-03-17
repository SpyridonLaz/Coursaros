import pickle
import sys
import time
from pathlib import Path

from tqdm import tqdm
from queue import Queue


from coursaros.edx.exceptions import EdxRequestError



class Collector:
    """
        Collects dict items that will be sent to the downloader later.
        Saves result in designated folders.
        Saves negative results.
        Saves result where a pdf file was created.
        """
    # TODO REWORK WITH PANDAS


    # ID's of previously found positive results.
    positive_results_id = set()

    # ID's of previously found negative results.
    negative_results_id = set()

    pdf_results_id = set()

    def __init__(self, save_to=Path.home()):
        self.save_results = save_to
        self.pdf = save_to
        self.positive = save_to
        self.negative = save_to
        self.downloads = Queue()
        self.positive1:{'id':Downloadable}=   dict()
        self.negative2 :{'id'}= dict()
        self.pdf3 :{'id'} = dict()
        # list of positive dictionary item objects that will be RETURNED to main()
        # for download
        self.results_to_write = ((self.positive,self.positive_results_id),
                            (self.pdf,self.pdf_results_id),
                            (self.negative,self.negative_results_id))


    def _load_previous_results(self,filepath, collection):
        if vars(self).get(collection,None) and filepath.stat().st_size!=0:
            # reads previously found negative and pdf results .
            with filepath.open("rb") as f:
                vars(self)[collection].update(pickle.load(f))

    @property
    def pdf(self):
        return self._pdf_results
    @property
    def positive(self):
        return self._positive

    @property
    def negative(self):
        return self._negative


    def _generic_path_setter(self, path, _type):
        path = Path(path, f'.Results_{_type}').resolve()
        path.touch(exist_ok=True)
        self._load_previous_results(path, f'{_type}_results_id')
        return path


    @pdf.setter
    def pdf(self, path):
        _type = 'pdf'
        path = path or self.save_results
        self._pdf_results = self._generic_path_setter(path, _type)


    @positive.setter
    def positive(self, path):
        _type= 'positive'
        path = path or self.save_results
        self._positive = self._generic_path_setter(path, _type)


    @negative.setter
    def negative(self, path):
        _type = 'negative'
        path = path or self.save_results
        self._negative = self._generic_path_setter(path, _type)




    def collect(self,item_id, url,filepath, *args,**kwargs ):
        '''
            param id: id of lecture/vertical
            param url: url of downloadable,
            param filepath: absolute filepath
            return: bool
		'''


        if  item_id not in self.positive_results_id:
            # avoids duplicates
            self.positive_results_id.add(item_id)
            item = Downloadable( filepath=filepath,
                                 url=url,
                                 ID =item_id)
            self.downloads.put_nowait(item)
            return item

    def save(self):

        return map(self.save_results,self.results_to_write)

    def save_results(self,results_to_write ):
        """
        return:list(dict()) self.downloads
          Saves all results in file to later reuse.
		"""

        from debug import DelayedKeyboardInterrupt
        with DelayedKeyboardInterrupt():
            for file, var_set in results_to_write:
                with file.open("wb") as f:
                    pickle.dump(var_set, f)
            print(f"SEARCH RESULTS SAVED IN {self.positive.parent}")



class Downloadable():
    # Chunk size to download videos in chunks
    VID_CHUNK_SIZE = 1024

    def __init__(self,
                 url: str,
                 filepath: str | Path,
                 ID: str | int):

        self.url = url
        self.filepath = Path(filepath)
        self._ID = ID





    @property
    def ID(self):
        return self._ID


    @staticmethod
    def file_exists(func):
        def inner(self,client):
            if not self.filepath.exists():
                # if file exists
                self.filepath.parent.mkdir(parents=True, exist_ok=True)
                func(self,client)
            else:
                print(f'Already downloaded. Skipping: {self.filepath.name}')


        return inner

    @file_exists
    def download(self,client ):


        print('Downloading: {name}'.format(name=self.filepath.name, ))
        # temporary name to avoid duplication.
        download_to_part = Path(f"{self.filepath}.part")
        # In order to make downloader resumable, we need to set our headers with
        # a correct Range path. we need the bytesize of our incomplete file and
        # the content-length from the file's header.

        current_size_file = download_to_part.stat().st_size if download_to_part.exists() else 0

        # print("url", url)
        # HEAD response will reveal length and url(if redirected).
        head_response = client.head(self.url,
                                         allow_redirects=True,
                                         timeout=60)

        url = head_response.url
        # file_content_length str-->int (remember we need to build bytesize range)
        file_content = int(head_response.headers.get('Content-Length', 0))

        progress_bar = tqdm(initial=current_size_file,
                            total=file_content,
                            unit='B',
                            unit_scale=True,
                            smoothing=0,
                            desc=f'{self.filepath.name}',
                            file=sys.stdout,
                            )
        # We set the progress bar to the size of already
        # downloaded .part file
        # to display the correct length.
        with client.get(url,
                            headers={'Range': f'bytes={current_size_file}-'},
                             stream=True,
                             allow_redirects=True,
                             ) as resp:

            with download_to_part.open( 'ab+') as f:
                for chunk in resp.iter_content(chunk_size=self.VID_CHUNK_SIZE * 100):
                    # -write response data chunks to file_content
                    # - Updates progress_bar
                    progress_bar.update(len(chunk))
                    f.write(chunk)

        progress_bar.close()
        #print(file_content_length,download_to_part.stat().st_size)
        if file_content == download_to_part.stat().st_size:
            # assuming downloaded file has correct number of bytes(size)
            # then we rename with correct suffix.
            Path.rename(download_to_part, self.filepath)
            #del self
            return True

        elif file_content < download_to_part.stat().st_size:
            print(f'Incomplete download. Removing: {self.filepath.name}')
            Path(download_to_part).unlink()
            return False
        else:
            return None


class KalturaDownloadable(Downloadable):
    def __init__(self,  url: str, save_as: str, ID:str|int ):

                                                            super().__init__( url=url, filepath=save_as,ID=ID)


    @staticmethod
    def _change_user_state(self,client):
        '''
        # Subtitles are either downloaded as (.srt) or as transcripts (.txt)
        # depending on  "user_state"  that is saved serverside, and we cannot
        # make the choice with a simple GET request.
        # Thus, a POST request is required , which will change the user state
        # to the following  "transcript_download_format": "srt".
        '''

        if Path(self.filepath).suffix == '.srt':

            for i in range(4):
                try:
                    save_user_state = self.url.replace("transcript", "xmodule_handler")
                    payload = {"transcript_download_format": "srt"}
                    response = client.post(
                        url=save_user_state,
                        cookies=client.cookies.get_dict(),
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
                        break



    def download(self,client):
        return super().download()
