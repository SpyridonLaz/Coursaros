from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from edx.EdxCourse import *
from SeleniumManager import *



try:
    from debug import LogMessage as log,Debugger as d
except ImportError:
    log = print
    d = print
    pass

class KalturaScraper(EdxCourse,):


    def __init__(self, context: Edx, slug: str = None, *args, ):
        super().__init__(context, slug, args)
        self.BASE_KALTURA_VIDEO_URL = None

    def scrape(self,  lecture_meta, soup):
        '''
        # we run a second client GET request by using
        # the parent's <iframe src="{nested iframe URL}"
        # attribute to dwelve deeper into it's nested content which will
        # eventually include both the video URL and subtitles URL.
        '''

        log("Entered experimental", 'green')
        driver = SeleniumManager(self.client.cookies)

        vertical_elements = soup.find_all('button', {'class': 'seq_other'})
        if vertical_elements:

            for vertical_elem in vertical_elements:
                vertical_slug = vertical_elem.get("data-id")

                if vertical_slug in (self.collector.positive_results_id | self.collector.negative_results_id):
                    log(f"{vertical_elem.get('data-path')} already parsed.")
                    log("Passing..", 'blue')
                    continue
                segment = re.sub(r'[^\w_ ]', '-', vertical_elem.get("data-page-title")).replace('/', '-')

                filepath = lecture_meta.get('filepath').format(segment=segment)


                vertical_url = "{}/{}".format(self.XBLOCK_BASE_URL, vertical_slug)
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
                            xview = WebDriverWait(driver.driver, 6).until(expected_conditions.presence_of_element_located((By.XPATH, xpath))
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
                                    pdf = Path(filepath).with_suffix('.pdf')
                                    Path(filepath).with_suffix('.pdf').exists()
                                    if check and not pdf.exists():
                                        inner_html = xview.get_attribute('innerHTML').replace('src="',
                                                                                              f'src="{self._PROTOCOL_URL}/'
                                                                                              )
                                        inner_html = inner_html.replace('src="https://courses.edx.org/http',
                                                                        'src="http'
                                                                        )
                                        try:
                                            self.collector.save_as_pdf(inner_html, filepath,
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
                    prepared_item.update(course_slug=self.slug,
                                         course=lecture_meta.get('course'),
                                         chapter=lecture_meta.get('chapter'),
                                         lecture=lecture_meta.get('display_name'),
                                         id=vertical_slug,
                                         segment=vertical_elem.get("data-page-title"),
                                         filepath=filepath,
                                         directory=lecture_meta.get('directory'))

                    # here we find the nescessary attributes
                    #  PID and entryID according to kalturaPlayer
                    #  official documentation.
                    PID = video_element.get_attribute('kpartnerid')
                    entryId = video_element.get_attribute('kentryid')
                    # build video url according to kaltura base URL.
                    video_url = self.BASE_KALTURA_VIDEO_URL.format(PID=PID,
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

                    self.collector(course=self.course_title,
                                   chapter=lecture_meta['chapter'],
                                   lecture=lecture_meta['display_name'],
                                   id=vertical_elem.get("data-id"),
                                   segment=vertical_elem.get("data-page-title"),
                                   )
                    self.collector(**prepared_item)
                else:
                    self.collector.negative_results_id.add(vertical_slug)
        return

