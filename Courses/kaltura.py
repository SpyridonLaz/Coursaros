import traceback
from pathlib import Path

import validators
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from Courses.EdxCourse import EdxCourse
from selenium_impl.SeleniumManager import SeleniumManager as sm



try:
    from debug import LogMessage as log,Debugger as d
    log = log()
    d = d()
except ImportError:
    log = print
    d = print
    pass

class KalturaScraper(EdxCourse,):
    BASE_KALTURA_VIDEO_URL = "https://cdnapisec.kaltura.com/p/{PID}/sp/{PID}00/playManifest/entryId/{entryId}/format/download/protocol/https/flavorParamIds/0"

    def __init__(self, context, slug: str = None, *args, ):
        super().__init__(context, slug, *args)
        self.driver = sm(self.connector)


    def scrape(self, lecture, lecture_meta, soup):
        '''
        # we run a second client GET request by using
        # the parent's <iframe src="{nested iframe URL}"
        # attribute to dwelve deeper into it's nested content which will
        # eventually include both the video URL and subtitles URL.
        '''

        log("Entered experimental", 'green')

        vertical_elements = soup.find_all('button', {'class': 'seq_other'})
        if vertical_elements:

            for vertical_elem in vertical_elements:
                vertical_slug = vertical_elem.get("data-id")

                if vertical_slug in (self.collector.positive_results_id | self.collector.negative_results_id):
                    log(f"{vertical_elem.get('data-path')} already parsed.")
                    log("Passing..", 'blue')
                    continue
                segment = self.sanitizer(vertical_elem.get("data-page-title"))
                _name = lecture_meta.get('path')
                name = f'{segment} - ' + _name.name
                filepath = Path(_name.parent, name)
                lecture_meta.update({'filepath': filepath})
                vertical_url = "{}/{}".format(self.urls.XBLOCK_BASE_URL, vertical_slug)
                log(f"Searching for elements in vertical block:  {vertical_elem.get('data-path')}")
                for i in range(1):
                    try:
                        self.driver.driver.get(vertical_url)
                        self.driver.cookies()
                    except:
                        log("No connection")
                    else:
                        try:
                            # xblock-student_view exists
                            xpath = "/html/body/div[4]/div/section/main/div[2]"
                            xview = WebDriverWait(self.driver.driver, 6).until(expected_conditions.presence_of_element_located((By.XPATH, xpath))
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

                                    inner_html = xview.get_attribute('innerHTML')
                                    try:
                                        self.collector.get_pdf(content = inner_html,
                                                               check = check,
                                                               path = filepath,
                                                               id=vertical_slug)

                                        log("PDF saved!", "orange")
                                    except Exception as e:
                                        print("Problem while building PDF.")
                                        print(e)

                            else:
                                log("Text content already parsed.Passing..", )
                            try:
                                print("searching for player")
                                WebDriverWait(self.driver.driver, 2).until(
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
                    video_element = WebDriverWait(self.driver.driver, 2).until(
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

                    #  we find the nescessary attributes
                    #  PID and entryID according to kalturaPlayer
                    #  official documentation.
                    PID = video_element.get_attribute('kpartnerid')
                    entryId = video_element.get_attribute('kentryid')
                    # build video url according to kaltura base URL.
                    video_url = self.urls.get_video_url(PID=PID, entryId=entryId)

                    self.collector.collect(
                        id=vertical_elem.get("data-id"),
                        url=video_url,
                        filepath=filepath.with_suffix('.mp4'))
                    log(
                        f"Struck gold! New video just found! {vertical_elem.get('data-page-title')}",
                        "orange"
                    )
                    if subtitle_element and validators.url(subtitle_element.get_attribute('src')):
                        log(
                            f"Subtitle found! {vertical_elem.get('data-page-title')}",
                            "orange"
                        )

                    self.collector.collect(
                        id=vertical_elem.get("data-id"),
                        url=subtitle_element.get_attribute('src'),
                        filepath=filepath.with_suffix('.srt'))
                else:
                    self.collector.negative_results_id.add(vertical_slug)
        return

