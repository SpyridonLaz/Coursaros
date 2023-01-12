from pathlib import Path

import pdfkit
import validators
import ast
from debug import LogMessage as log, Debugger as d , DelayedKeyboardInterrupt
from edx.Urls import EdxUrls as edx
class Collector(edx):
    # todo olo
    all_videos = []

    # ID's of previously found positive results.
    positive_results_id = set()

    # ID's of previously found negative results.
    negative_results_id = set()

    pdf_results_id = set()
    def __init__(self,):
        """
		Collects dict items that will be sent to the downloader later.
		Saves result in designated folders.
		Saves negative results.
		Saves result where a pdf file was created.
		"""

        # list of positive dictionary item objects that will be RETURNED to main()
        # for download
        print("THIS IS A PATH OR NOT  ??",self.BASE_FILEPATH)
        self.pdf_results = self.BASE_FILEPATH.as_uri().format(file='.{self.platform}PDFResults')

        self.results = self.BASE_FILEPATH.as_uri().format(file='.{self.platform}Results')
        self.negative_results = self.BASE_FILEPATH.as_uri().format(file='.edxResults_bad')

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
                 video_url, filepath,):
        '''
            param id: id of current block where item was found
            param course: name of EdxCourse,
            param course_slug: slug of course
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

    def save_as_pdf(self, content: str, path: str, id: str):
        '''
        :param string: string-like data to be made into PDF
        :param path: full path save directory
        :param id: id of page where the data was found.
        :return: None
        '''
        pdf_save_as = Path(path)
        pdfkit.from_string(content, output_path=pdf_save_as)
        self.pdf_results_id.add(id)

