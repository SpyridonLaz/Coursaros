import ast
import html
import json
import os
import pickle
import re
import sys
import time
import traceback
from os.path import expanduser
import concurrent.futures
import colorful as cf
import pdfkit
import requests
import validators
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from Exceptions import *

try:
    from  debug import *
    #this is basically a print with a counter
    d = Debugger()
except ImportError:
    d = print
    pass

#

# Chunk size to download videos in chunks
VID_CHUNK_SIZE = 1024




class EdxDownloader:
	# TODO
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
	VERTICAL_BASE_URL = '{}/course_dir'.format(LMS_BASE_URL)
	DOWNLOAD_KALTURA_URL = "https://cdnapisec.kaltura.com/p/{PID}/sp/{PID}00/playManifest/entryId/{entryId}/format/download/protocol/https/flavorParamIds/0"

	# Create a request session to send cookies
	# automatically for HTTP requests.

	# Generate a fake user-agent to avoid blocks
	user_agent = UserAgent()

	# Initiate webdriver

	# These headers are required. Some may not be required
	# but sending all is a good practice.
	edx_headers = {
			'Host'            : EDX_HOSTNAME,
			'accept'          : '*/*',
			'x-requested-with': 'XMLHttpRequest',
			'user_agent'      : 'Mozilla/5.0 (X11; Linux x86_64) '
								'AppleWebKit/537.36 (KHTML, like Gecko) '
								'Chrome/101.0.4951.54 Safari/537.36',
			# 'user-agent': user_agent.random,
			# 'user-agent': driver.execute_script("return navigator.userAgent"),
			'content-type'    : 'application/x-www-form-urlencoded; charset=UTF-8',
			'origin'          : BASE_URL,
			'sec-fetch-site'  : 'same-origin',
			'sec-fetch-mode'  : 'cors',
			'sec-fetch-dest'  : 'empty',
			'referer'         : LOGIN_URL,
			'accept-language' : 'en-US,en;q=0.9',
			'connection'      : 'keep-alive',
			'Keep-Alive'      : 'timeout=30, max=10000'
	}



	def __init__(self, email, password, ):
		# This is set True later and is used to
		# avoid unnecessary login attempts
		self.is_authenticated = False
		# CookieHandler with pickle module
		self.client = requests.Session()
		# CollectorUrls
		self.collector = Collector()
		# The EDX account's email
		self.edx_email = email
		# The EDX account's password
		self.edx_password = password
		# Enables experimental parser for specific Courses that embed Kaltura WebPlayer.
		self.toggle_experimental = toggle_experimental

	def load(self, ):
		if self.session_file_exists and os.path.getsize(self.SAVED_SESSION_PATH) > 100:
			with open(self.SAVED_SESSION_PATH, 'rb') as f:
				self.client = pickle.load(f)
			return True
		else:
			log("pickleJar is empty", "red")
			return False

	def dump(self, ):
		with open(self.SAVED_SESSION_PATH, 'wb') as f:
			pickle.dump(self.client, f)

	def sign_in(self):
		# Authenticates the user session. It returns True on success
		# or raises EdxLoginError on failure.
		# html_res = self.requests_session.get(_LOGIN_URL)
		# Retrieve the CSRF token first

		try:
			self.client.get(LOGIN_URL)  # sets cookie
			if 'csrftoken' in self.client.cookies:
				# Django 1.6 and up
				csrftoken = self.client.cookies['csrftoken']

			else:
				# older versions
				csrftoken = self.client.cookies['csrf']

			self.edx_headers.update({'x-csrftoken': csrftoken})
			data = {
					'email'   : self.edx_email,
					'password': self.edx_password
			}
			res = self.client.post(LOGIN_API_URL, headers=self.edx_headers, data=data).json()

			if res.get('success') is True:
				self.is_authenticated = True
				return True
			else:
				if res.get("path"):
					raise EdxLoginError(res.get('path'))
		except ConnectionError as e:
			print(e)
			raise EdxRequestError("Connection or CSRF token problem")

	def experimental_scrape(self, lecture_meta, course_slug, soup):
		'''
		# we run a second client GET request by using
		# the parent's <iframe src="{nested iframe URL}"
		# attribute to dwelve deeper into it's nested content which will
		# eventually include both the video URL and subtitles URL.
		'''
		log("Entered experimental",'green')
		driver = SeleniumManager(self.client.cookies)

		vertical_elements = soup.find_all('button', {'class': 'seq_other'})
		if vertical_elements:


			for vertical_elem in vertical_elements:
				vertical_slug = vertical_elem.get("data-id")

				if vertical_slug in (self.collector.positive_results_id | self.collector.negative_results_id):
					log(f"{vertical_elem.get('data-path')} already parsed.")
					log(" Passing..", 'red')
					continue
				segment = re.sub(r'[^\w_ ]', '-', vertical_elem.get("data-page-title")).replace('/', '-')

				vertical_base_filename = lecture_meta.get('base_filename').format(segment=segment)

				total_file_path = '{}/{}'.format(lecture_meta.get("base_directory"), vertical_base_filename)

				vertical_url = "{}/{}".format(XBLOCK_BASE_URL, vertical_slug)
				log(f"Searching for elements in vertical block:  {vertical_elem.get('data-path')}")
				for i in range(1):
					try:
						driver.driver.get(vertical_url)
						driver.loadCookies()
					except:
						log("No connection")
					else:
						try:
							# xblock-student_view exists
							xpath = "/html/body/div[4]/div/section/main/div[2]"
							xview = WebDriverWait(driver.driver, 6).until(
									expected_conditions.presence_of_element_located((By.XPATH, xpath))
							)
						except TimeoutException:
							self.collector.negative_results_id.add(vertical_slug)
							print("Content of no importance")
							continue
						except:
							print(traceback.format_exc())
							print("ERROR PROBLEM CHECK IT ")
							continue
						else:
							if vertical_slug not in self.collector.pdf_results_id:
								try:
									# check if xblock contains paragraphs, if True, then we make PDF
									check = WebDriverWait(xview, 1).until(
											expected_conditions.presence_of_element_located((By.TAG_NAME, 'p'))
									)

								except:
									print("No available paragraphs for PDF creation")
								else:
									if check and not os.path.exists(total_file_path + '.pdf'):
										inner_html = xview.get_attribute('innerHTML').replace('src="',
																							  'src="https://courses.edx.org/'
																							  )
										inner_html = inner_html.replace('src="https://courses.edx.org/http',
																		'src="http'
																		)
										try:
											self.collector.save_as_pdf(inner_html, total_file_path,
																	   id=vertical_slug
																	   )
											log("PDF saved!", "orange")
										except Exception as e:
											print("Problem while building PDF.")
											print(e)
										else:
											self.collector.pdf_results_id.add(vertical_slug)
									else:
										log('PDF file already saved.Passing..', )
							else:
								log("Text content already parsed.Passing..", )
							try:
								print("searching for player")
								WebDriverWait(driver.driver, 2).until(
										expected_conditions.frame_to_be_available_and_switch_to_it(
												(By.ID, "kaltura_player")
										)
								)
							except:
								print("No available Video")
								continue
							# except TimeoutException:
							#     continue
							# except NoSuchElementException:
							#     print(traceback.format_exc())
							#     print("ERROR NO SUCH ELEMENT")
							else:
								log("Switching to iframe")
								break

				else:
					self.collector.negative_results_id.add(vertical_slug)
					continue

				try:
					video_element = WebDriverWait(driver.driver, 2).until(
							expected_conditions.presence_of_element_located((By.ID, "pid_kaltura_player"))
					)
				except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
					log(f"Error while grabing video.{e}", 'red')
					if i < 1:
						log("Retrying..")
					continue
				else:
					# video found
					subtitle_element = None
					try:
						subtitle_element = video_element.find_element(By.TAG_NAME, 'track')
					except (NoSuchElementException, StaleElementReferenceException):
						log("Subtitle was not found for this video")
				if video_element:
					# video exists so we start to build our download item
					# which will be added to download queue later.
					prepared_item = {}
					prepared_item.update(course_slug=course_slug,
										 course=lecture_meta.get('course_dir'),
										 chapter=lecture_meta.get('chapter'),
										 lecture=lecture_meta.get('display_name'),
										 id=vertical_slug,
										 segment=vertical_elem.get("data-page-title"),
										 base_filename=vertical_base_filename,
										 base_directory=lecture_meta.get('base_directory'))

					# here we find the nescessary attributes
					#  PID and entryID according to kalturaPlayer
					#  official documentation.
					PID = video_element.get_attribute('kpartnerid')
					entryId = video_element.get_attribute('kentryid')
					# build video url according to kaltura base URL.
					video_url = BASE_KALTURA_VIDEO_URL.format(PID=PID,
															  entryId=entryId)

					prepared_item.update(video_url=video_url)
					log(
							f"Struck gold! New video just found! {vertical_elem.get('data-page-title')}",
							"orange"
					)
					if subtitle_element and validators.url(subtitle_element.get_attribute('src')):
						log(
								f"Subtitle found! {vertical_elem.get('data-page-title')}",
								"orange"
						)
						prepared_item.update(subtitle_url=subtitle_element.get_attribute('src'))

					# self.collector(course_dir=_course_dir,
					#                chapter=lecture_meta['chapter'],
					#                lecture=lecture_meta['display_name'],
					#                id=vertical_elem.get("data-id"),
					#                segment=vertical_elem.get("data-page-title"),
					#                )
					self.collector(**prepared_item)
				else:
					self.collector.negative_results_id.add(vertical_slug)
		return

	def dashboard_urls(self):
		'''
		The following function scrapes the main dashboard for all available courses
		including archived.
		It does NOT parse courses with invalid or expired access.

		'''
		available_courses = []
		try:
			response = self.client.get(DASHBOARD_URL,
									   headers=self.edx_headers)
		except ConnectionError as e:
			raise EdxRequestError(str(e))

		soup = BeautifulSoup(html.unescape(response.text), 'lxml')
		soup_elem = soup.find_all('a', {'class': 'enter-course_dir'})
		if soup_elem:
			for i, element in enumerate(soup_elem):
				course_slug = element.get('data-course_dir-key')

				course_title = soup.find('h3', {'class': 'course_dir-title',
												'id'   : 'course_dir-title-' + course_slug}
										 )
				print(course_title)
				course_title= course_title.text.strip()
				course_url = "{}/{}/".format(COURSE_BASE_URL, course_slug)
				available_courses.append({'course_dir': course_title,
										  'course_url'  : course_url,
										  'course_slug' : course_slug}
										 )
		if len(available_courses) :
			# print(available_courses)
			log(f"{len(available_courses)} available courses found in your Dashboard!", 'orange')
		else:
			log("No courses available!", "red")
		return available_courses

	def get_course_data(self, course_url: str):
		'''

		 This method expects a course_dir's URL as argument, searches for it's xBlock structure and, if found, it returns it as a dictionary,else raises exception.
		'''

		log('Building xblocks.')
		# TODO  URL CHECK START
		# Break down the given course_dir URL to get the course_dir slug.
		course_slug = course_url
		if not course_url.startswith('course_dir-'):
			url_parts = course_url.split('/')
			for part in url_parts:
				if part.startswith('course_dir-'):
					course_slug = part
					break
			else:
				# If the conditions above are not passed, we will assume that a wrong
				# course_dir URL was passed in.
				raise EdxInvalidCourseError('The provided course_dir URL seems to be invalid.')
		# if course_slug in self.collector.negative_results_id:
		# 	return

		# Construct the course_dir outline URL
		COURSE_OUTLINE_URL = '{}/{}'.format(COURSE_OUTLINE_BASE_URL, course_slug)
		# TODO   URL CHECK STOP

		# TODO xBlockMapper start

		# Make an HTTP GET request to outline URL
		# and return a dictionary object
		# with blocks:metadata as key:values which
		# will help us iterate through course_dir.

		try:
			outline_resp = self.client.get(COURSE_OUTLINE_URL,
										   headers=self.edx_headers)
		except ConnectionError as e:
			raise EdxRequestError(e)
		# Transforms response into dict and returns the course_dir's block structure into variable 'blocks'.
		# blocks:metadata as keys:values
		try:
			blocks = outline_resp.json()
		except Exception as e:
			print(traceback.format_exc())
			sys.exit(1)
		if blocks is None:
			# If no blocks are found, we will assume that the user is not authorized
			# to access the course_dir.
			raise EdxNotEnrolledError('No course_dir content was found. Check your enrollment status and try again.')
		else:
			blocks = blocks.get('course_blocks').get('blocks')

		course_title = None
		if list(blocks.values())[0].get('type') == 'course_dir':
			course_title = list(blocks.values())[0].get('display_name')
		else:
			for block, block_meta in blocks.items():
				if block_meta.get('type') == 'course_dir' and block_meta.get('display_name') is not None:
					course_title = block_meta.get('display_name')
					break

		lectures = {k: v for k, v in blocks.items() if v['type'] == 'sequential'}
		chapters = {k: v for k, v in blocks.items() if v['type'] == 'chapter' and v['children'] is not None}

		# course_dir directory
		course_name = re.sub(r'[^\w_ ]', '-', course_title).replace('/', '-').strip()
		main_dir = os.path.join(os.getcwd(),'edx' ,course_name)
		if not os.path.exists(main_dir):
			# create course_dir Directory
			os.makedirs(main_dir)


		for i, (lecture, lecture_meta) in enumerate(lectures.items()):
			lecture_name = re.sub(r'[^\w_ ]', '-', lecture_meta.get('display_name')).replace('/', '-')
			for chapter, chapter_meta in chapters.items():
				if lecture in chapter_meta.get('children'):
					chapter_name = re.sub(r'[^\w_ ]', '-', chapter_meta.get('display_name')).replace('/', '-').strip()
					chapter_dir = os.path.join(main_dir, chapter_name)
					if not os.path.exists(chapter_dir):
						# create lecture Directories
						os.makedirs(chapter_dir)

					lecture_meta.update({'chapter': chapter_meta.get('display_name')})
					lecture_meta.update({'chapterID': chapter_meta.get('id')})
					lecture_meta.update({'course_dir': course_title})

					base_filename = '{segment} - ' + f'{lecture_name}'
					lecture_meta.update({'base_filename': base_filename})
					lecture_meta.update({'base_directory': chapter_dir})


			# assuming that _lectures are ordered .

			lecture_url = "{}/{}".format(XBLOCK_BASE_URL, lecture)
			print(lecture_url)

			# TODO xBlockMapper STOP
			soup = None
			for j in range(3):
				try:
					lecture_res = self.client.get(lecture_url,
												  headers=self.edx_headers,
												  allow_redirects=True)
					soup = BeautifulSoup(html.unescape(lecture_res.text), 'lxml')
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

				if self.toggle_experimental:
					self.experimental_scrape(lecture_meta, course_slug, soup)

				else:
					self.scrape(lecture, lecture_meta, course_slug, soup)
			except (KeyboardInterrupt, ConnectionError):
				self.collector.save_results()

			self.collector.negative_results_id.add(lecture)
		else:
			self.collector.negative_results_id.add(course_slug)

	def scrape(self, lecture, lecture_meta, course_slug, soup):
		'''
		# Searches through HTML elements
		# Finds and builds URLs for subtitles and videos
		'''
		log("Entered Default")
		# iframe_soup = soup.find('iframe', {'id':'unit-iframe'})
		# if iframe_soup:
		# 	segment = iframe_soup.get('title')
		# 	segment_title = re.sub(r'[^\w_ ]', '-', segment).replace('/', '-')

		base_directory = lecture_meta.get('base_directory')

		for i in soup.find_all('div', {'class': 'xblock-student_view-video'}):

			header_block = i.find('h3', attrs={'class': 'hd hd-2'})
			if header_block:
				segment_title = re.sub(r'[^\w_ ]', '-', header_block.text).replace('/', '-')
				base_filename = lecture_meta.get('base_filename').format(segment=segment_title)
				total_file_path = os.path.join(base_directory, base_filename)
				print(base_filename)



				paragraphs =  i .find_all('p')



				if paragraphs  and not os.path.exists(total_file_path+ '.pdf'):
					inner_html = i.decode_contents().replace('src="',
																		  'src="https://courses.edx.org/')
					inner_html = inner_html.replace('src="https://courses.edx.org/http','src="http')
					try:
						self.collector.save_as_pdf(inner_html, total_file_path,
												   id=lecture
												   )
						log("PDF saved!", "orange")
					except Exception as e:
						print("Problem while building PDF.")
						print(e)



				meta_block = i.find('div', {'class': 'video', 'data-metadata': True})

				if meta_block :


					json_meta = json.loads(meta_block.get('data-metadata'))
					# Get the data-metadata attribute HTML
					# and parse it as a JSON object.
					prepared_item = {}
					if 'sources' in json_meta:

						for video_source in list(json_meta['sources']):
							if video_source.endswith('.mp4'):
								# video URL found
								log(f"Struck gold! A video was found in segment: {base_filename}!",
									"orange"
									)
								log(video_source,
									"orange"
									)
								prepared_item.update(course_slug=course_slug,
													 course=lecture_meta.get('course_dir'),
													 chapter=lecture_meta.get('chapter'),
													 lecture=lecture_meta.get('display_name'),
													 id=lecture,
													 segment=segment_title,
													 base_directory=base_directory,
													 video_url=video_source,
													 base_filename=base_filename)

								# Break the loop if a valid video URL
								# is found.
								subtitle_url=''
								if 'transcriptAvailableTranslationsUrl' in json_meta:
									# subtitle URL found
									subtitle_url = '{}{}'.format(BASE_URL,
																 json_meta.get('transcriptAvailableTranslationsUrl')
																 .replace("available_translations", "download")
																 )
									log(f"Subtitle was found for: {base_filename}!",
										"orange"
										)
								prepared_item.update(subtitle_url=subtitle_url)

								self.collector(**prepared_item)
		return


class Collector():
	base_filepath = os.path.join(expanduser('~'), '{file}')

	def __init__(self):
		"""
		Collects dict items that will be sent to the downloader later.
		Saves results in designated folders.
		Saves negative results.
		Saves results where a pdf file was created.
		"""

		# list of positive dictionary item objects that will be RETURNED to main()
		# for download
		self.all_videos = []

		# set with ID's of previously found positive dictionary results.
		self.positive_results_id = set()

		# set with ID's of previously found negative dictionary results.
		self.negative_results_id = set()
		# TEST
		self.pdf_results_id = set()
		self.pdf_results = self.base_filepath.format(file='.edxPDFResults')

		self.results = self.base_filepath.format(file='.edxResults')
		self.negative_results = self.base_filepath.format(file='.edxResults_bad')

		with open(self.results, "r") as f:
			# reads previously found positive results .
			for line in f:
				d = ast.literal_eval(line)
				if not d.get('id',None) in self.positive_results_id:
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

	def __call__(self, id, course, course_slug, chapter, lecture, segment,
				 video_url, base_filename, base_directory, subtitle_url=''):
		'''
		:param id: id of current block where item was found
		:param course: name of EdxCourse,
		:param course_slug: slug of course_dir
		:param chapter: current chapter
		:param lecture: lecture (sequence)
		:param segment: Segment or video name
		:param video_url:  video url
		:param base_filename: base filename, without suffix
		:param base_directory: directory of file
		:param subtitle_url:  subtitle url
		:return: bool
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

	# class downloadable:
	# 	def __init__( self ):
	# 		self.id =
	# 		self.course_dir=
	# 		self.course_slug=
	# 		self.chapter=
	# 		self.lecture=
	# 		self.segment=
	# 		self.video_url=
	# 		self.subtitle_url=
	# 		self.base_filename=
	# 		self.base_directory=
	#
	# 	def __call__( self,  *args , **kwargs):
	# 		'''
	# 		:param id: id of current block where item was found
	# 		:param course_dir: name of EdxCourse,
	# 		:param course_slug: slug of course_dir
	# 		:param chapter: current chapter
	# 		:param lecture: lecture (sequence)
	# 		:param segment: Segment or video name
	# 		:param video_url:  video url
	# 		:param base_filename: base filename, without suffix
	# 		:param base_directory: directory of file
	# 		:param subtitle_url:  subtitle url
	# 		:return: bool
	# 		'''
	#
	# 		d = dict(i for i in args if i in ('id', 'course_dir',
	# 										'course_slug', 'chapter',
	# 										'lecture', 'segment',
	# 										'video_url', 'base_filename',
	# 										'base_directory', 'subtitle_url' ) and )
	#
	#
	# 		item = locals()
	# 		item.pop('self')
	# 		if item.get('id') not in self.positive_results_id:
	# 			# avoids duplicates
	# 			if not validators.url(item.get('subtitle_url')):
	# 				item.pop('subtitle_url')
	#
	# 			self.all_videos.append(item)
	# 			self.positive_results_id.add(item.get('id'))
	# 			print(len(self.all_videos))
	# 			return True
	# 		else:
	# 			return False

	def save_results(self, ):
		'''
		:return:list(dict()) self.all_videos
		Saves all results in file to later reuse.
		'''

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

		return self.all_videos

	def save_as_pdf(self, string: str, path: str, id: str):
		'''

		:param string: string-like data to be made into PDF
		:param path: full path save directory
		:param id: id of page where the data was found.
		:return: None
		'''
		# course_dir directory
		# pdf_options = {'cookie': [('csrftoken', token)]}

		pdf_save_as = f'{path}.pdf'
		pdfkit.from_string(string, output_path=pdf_save_as)
		self.pdf_results_id.add(id)




class Downloader():
	def __init__(self, client: requests.Session, url: str, save_as: str, desc: str, srt:bool= False ):

		self.client = client
		self.url = url
		self.save_as = save_as
		self.desc = desc
		self.headers = {'x-csrftoken': self.client.cookies.get_dict().get('csrftoken')}
		self.srt = srt


	@staticmethod
	def file_exists( func):
		def inner(self):
			if os.path.exists(self.SAVE_TO):
				# if file exists
				log(f'Already downloaded. Skipping: {self.desc}.{self.SAVE_TO.split(".")[-1:]}')
				return False
			func(self)
		return inner

	@staticmethod
	def deco(func):
		def inner (self):
			if self.srt and 'kaltura' not in self.url:
				self.change_user_state()
			func(self)
		return inner

	def change_user_state(self,):
		'''
		# Subtitles are either downloaded as (.srt) or as transcripts (.txt)
		# depending on  "user_state"  that is saved server side and we cannot
		# make the choice with a simple GET request.
		# Thus, a POST request is required , which will change the user state
		# to the following  "transcript_download_format": "srt".
		'''

		for i in range(4):
			try:
				save_user_state = self.url.replace("transcript", "xmodule_handler").replace("download", "save_user_state")
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
	@deco
	def download(self, ):
		s= 'srt' if self.srt else 'mp4'
		log('Downloading: {name}.{srt}'.format(name=self.desc, srt=s))
		# temporary name to avoid duplication.
		save_as_parted = f"{self.save_as}.part"
		# In order to make downloader resumable, we need to set our headers with
		# a correct Range path. we need the bytesize of our incomplete file and
		# the content-length from the file's header.

		current_size_file = os.path.getsize(save_as_parted) if os.path.exists(save_as_parted) else 0
		range_headers = {'Range': f'bytes={current_size_file}-'}

		# print("url", url)
		# HEAD response will reveal length and url(if redirected).
		head_res = self.client.head(self.url,
									headers=self.headers.update(range_headers),
									allow_redirects=True,
									timeout=60)

		url = head_res.url
		# file_size str-->int (remember we need to build bytesize range)
		file_size = int(head_res.headers.get('Content-Length', 0))

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
				for chunk in resp.iter_content(chunk_size=VID_CHUNK_SIZE * 100):
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

