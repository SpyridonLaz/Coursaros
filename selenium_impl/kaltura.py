 
import os
import re
import traceback

import validators
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from SeleniumManager import *
from scraper import Course


class KalturaScraper(Course):

    def __init__(self, client, lecture_meta, course_slug, soup, ):


        self.soup = soup
        self.course_slug = course_slug
        self.lecture_meta = lecture_meta

    def scrape(self, ):
        '''
        # we run a second client GET request by using
        # the parent's <iframe src="{nested iframe URL}"
        # attribute to dwelve deeper into it's nested content which will
        # eventually include both the video URL and subtitles URL.
        '''

        self.context.log("Entered experimental", 'green')
        driver = SeleniumManager(self.client.cookies)

        vertical_elements = self.soup.find_all('button', {'class': 'seq_other'})
        if vertical_elements:

            for vertical_elem in vertical_elements:
                vertical_slug = vertical_elem.get("data-id")

                if vertical_slug in (self.collector.positive_results_id | self.collector.negative_results_id):
                    self.context.log(f"{vertical_elem.get('data-path')} already parsed.")
                    self.context.log("Passing..", 'blue')
                    continue
                segment = re.sub(r'[^\w_ ]', '-', vertical_elem.get("data-page-title")).replace('/', '-')

                vertical_base_filename = self.lecture_meta.get('base_filename').format(segment=segment)

                total_file_path = '{}/{}'.format(self.lecture_meta.get("base_directory"), vertical_base_filename)

                vertical_url = "{}/{}".format(self.context.XBLOCK_BASE_URL, vertical_slug)
                self.context.log(f"Searching for elements in vertical block:  {vertical_elem.get('data-path')}")
                for i in range(1):
                    try:
                        driver.driver.get(vertical_url)
                        driver.loadCookies()
                    except:
                        self.context.log("No connection")
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
                                            self.context.log("PDF saved!", "orange")
                                        except Exception as e:
                                            print("Problem while building PDF.")
                                            print(e)
                                        else:
                                            self.collector.pdf_results_id.add(vertical_slug)
                                    else:
                                        self.context.log('PDF file already saved.Passing..', )
                            else:
                                self.context.log("Text content already parsed.Passing..", )
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
                                self.context.log("Switching to iframe")
                                break

                else:
                    self.collector.negative_results_id.add(vertical_slug)
                    continue

                try:
                    video_element = WebDriverWait(driver.driver, 2).until(
                        expected_conditions.presence_of_element_located((By.ID, "pid_kaltura_player"))
                    )
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
                    self.context.log(f"Error while grabing video.{e}", 'red')
                    if i < 1:
                        self.context.log("Retrying..")
                    continue
                else:
                    # video found
                    subtitle_element = None
                    try:
                        subtitle_element = video_element.find_element(By.TAG_NAME, 'track')
                    except (NoSuchElementException, StaleElementReferenceException):
                        self.context.log("Subtitle was not found for this video")
                if video_element:
                    # video exists so we start to build our download item
                    # which will be added to download queue later.
                    prepared_item = {}
                    prepared_item.update(course_slug=self.course_slug,
                                         course=self.lecture_meta.get('course'),
                                         chapter=self.lecture_meta.get('chapter'),
                                         lecture=self.lecture_meta.get('display_name'),
                                         id=vertical_slug,
                                         segment=vertical_elem.get("data-page-title"),
                                         filename=vertical_base_filename,
                                         directory=self.lecture_meta.get('base_directory'))

                    # here we find the nescessary attributes
                    #  PID and entryID according to kalturaPlayer
                    #  official documentation.
                    PID = video_element.get_attribute('kpartnerid')
                    entryId = video_element.get_attribute('kentryid')
                    # build video url according to kaltura base URL.
                    video_url = self.context.BASE_KALTURA_VIDEO_URL.format(PID=PID,
                                                                           entryId=entryId)

                    prepared_item.update(video_url=video_url)
                    self.context.log(
                        f"Struck gold! New video just found! {vertical_elem.get('data-page-title')}",
                        "orange"
                    )
                    if subtitle_element and validators.url(subtitle_element.get_attribute('src')):
                        self.context.log(
                            f"Subtitle found! {vertical_elem.get('data-page-title')}",
                            "orange"
                        )
                        prepared_item.update(subtitle_url=subtitle_element.get_attribute('src'))

                    # self.collector(course=course_title,
                    #                chapter=lecture_meta['chapter'],
                    #                lecture=lecture_meta['display_name'],
                    #                id=vertical_elem.get("data-id"),
                    #                segment=vertical_elem.get("data-page-title"),
                    #                )
                    self.collector(**prepared_item)
                else:
                    self.collector.negative_results_id.add(vertical_slug)
        return
