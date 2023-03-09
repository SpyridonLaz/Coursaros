import sys
import time
from queue import Queue

import requests
from requests import HTTPError, exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium_impl.selenium_manager import SeleniumSession
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append('..')
import html

from Platforms.base_platform import BasePlatform

from Courses.edx_course import EdxCourse
from exceptions import EdxRequestError, EdxLoginError
from Urls.edx_urls import EdxUrls


class Edx(BasePlatform,   SeleniumSession,):
    is_authenticated =BasePlatform.is_authenticated
    _courses =[]
    courses_found = []
    scanned = False
    def __init__(self, email: str, password: str, driver = True , **kwargs):

        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         **kwargs)

        SeleniumSession.__init__(self ,driver=driver,)

        if kwargs.get('driver'):

            self.init_driver()
            self.main_tab = self.driver.current_window_handle
            self.client.headers.update({'User-Agent': self.user_agent(),'Referer':self.urls.DASHBOARD_URL})

    @staticmethod
    def logged_in(selenium):
        """ Decorator to check if the user is logged in """

        def wrapper(func):
            def nested_wrapper(self, *args, **kwargs):

                if self.login_status(selenium):
                    return func(self, *args, **kwargs)
                else:
                    self.log("Please login first!")
                    return False

            return nested_wrapper

        return wrapper

    @staticmethod
    def with_driver(func):
        def wrapper(self, *args, **kwargs):
            if not self.driver:
                print("Initiate WebDriver first.")
                return False
            else:
                return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def is_scanned(func):
        """ Decorator to check if the dashboard has been scanned for courses"""

        def wrapper(self, *args, **kwargs):
            if self.scanned:
                return func(self, *args, **kwargs)
            else:
                self.log("Please scan the dashboard first!", "red")
                return False

        return wrapper

    @logged_in(selenium=True)

    @with_driver
    def dashboard_lookup(self,*args, **kwargs):
        '''
        The main function to scrape the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired, not enrolled or
        unavailable for any reason.

        returns: A list with the URLs of all available courses.
        '''
        try:
            print("Retrieving courses from Dashboard...Please wait...")

            self._ensure_url(self.urls.DASHBOARD_URL)
        except HTTPError as e:
            raise EdxLoginError(f"Login failed. Please check your credentials.Error : {e}")

        except exceptions.RequestException as e:
            raise EdxLoginError(f"Login failed. Error : {e}")
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        while True:
            course_cards = self.driver.find_elements(By.CLASS_NAME, 'course-card')
            print(len(course_cards))
            for course_card in course_cards:
                slug , title = None, None
                time.sleep(0.1)
                # time.sleep(2222222)
                inactive = course_card.find_element(By.CLASS_NAME,"btn.btn-primary").get_attribute("aria-disabled")
                if not inactive=="true":
                    _elem = course_card.find_element(By.CLASS_NAME, 'course-card-title')
                    title = _elem.text
                    # startswith('course-v1')
                    _split= [   x for x in _elem.get_attribute('href').split('/') if x.startswith('course-v1')]
                    try:
                        slug = _split[0]
                    except IndexError:
                        print("INDEX ERROR  - DASHBOARD URLS")
                        continue

                    print (inactive,title, slug)
                    if slug and title :
                        self.courses_found.append((slug , title))

            try:
                next_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,'//button[(contains(@class,"btn-icon"))  and (contains(@class,"next")) and (not (@disabled))]'))   )
            except TimeoutException:
                print("No more pages")

                break
            else:
                self.driver.execute_script("arguments[0].click();",next_btn)
                time.sleep(2)
        # time.sleep(400000)
        self.scanned = True
        if len(self.courses_found) > 0:
            print("DONE", self.courses_found)
            self.log(f"{len(self.courses_found)} available courses found in your Dashboard!", 'orange')
            return enumerate(self._courses)
        else:
            self.log("No courses available!", "red")
    @logged_in(selenium=False)
    def dashboard_lookup_api(self, *args, **kwargs):

        """ dashboard_api with requests """
        cookies= ""
        for cookie in self.client.cookies.get_dict().items():
            cookies += f"{cookie[0]}={cookie[1]};"

        self.client.headers.update({'cookie':cookies})
        a= requests.Session()










        # self.client.headers.update({'x-csrftoken':"Gi6bugECkDMg1aeAEAQbyFF1G7lt8PLrPSuS8WHHYxxAgfyuJYwG8jQcvUoaP3Mw"})
        # self.client.headers.update({ 'user-agent': self.user_agent()})
        # self.client.headers.update({ 'cookie':"cookie: _gcl_au=1.1.715966667.1678064068; __zlcmid=1EkleKCjw0hxyBL; OptanonAlertBoxClosed=2023-03-06T00:55:53.231Z; optimizelyEndUserId=oeu1678064153426r0.05886705418110871; _ga=GA1.2.1712811215.1678064155; _gid=GA1.2.264416533.1678064155; ajs_anonymous_id=f3895823-e396-42f3-96c6-beccd179c4e3; hubspotutk=da5e97b673d39d0de95d03f7e9f51741; _tt_enable_cookie=1; _ttp=HsWuYvLv6yrRgxzDixUregMNduQ; _fbp=fb.1.1678064155704.1422811227; _hjSessionUser_1563632=eyJpZCI6IjJlZjAwMTZhLTI2N2UtNWQ3Zi1hN2MwLWZiYmU3OTQzNGRjNCIsImNyZWF0ZWQiOjE2NzgwNjQxNTU2MTEsImV4aXN0aW5nIjp0cnVlfQ==; edxloggedin=true; prod-edx-user-info=\"{\"version\": 1\054 \"username\": \"SpeedySnail\"\054 \"email\": \"l2lords@yahoo.gr\"\054 \"header_urls\": {\"logout\": \"https://courses.edx.org/logout\"\054 \"account_settings\": \"https://courses.edx.org/account/settings\"\054 \"learner_profile\": \"https://courses.edx.org/u/SpeedySnail\"\054 \"resume_block\": \"https://courses.edx.org/courses/course-v1:KULeuvenX+WEBSECx+3T2017/jump_to/block-v1:KULeuvenX+WEBSECx+3T2017+type@html+block@53aa3abc2730478da12ac32d05f37845\"}\054 \"user_image_urls\": {\"full\": \"https://prod-edx-edxapp-assets.edx-cdn.org/static/edx.org-next/images/profiles/default_500.3292bbf079b8.png\"\054 \"large\": \"https://prod-edx-edxapp-assets.edx-cdn.org/static/edx.org-next/images/profiles/default_120.7c4c5c6b90a1.png\"\054 \"medium\": \"https://prod-edx-edxapp-assets.edx-cdn.org/static/edx.org-next/images/profiles/default_50.d29941819645.png\"\054 \"small\": \"https://prod-edx-edxapp-assets.edx-cdn.org/static/edx.org-next/images/profiles/default_30.ee82223aa027.png\"}}\"; csrftoken=Gi6bugECkDMg1aeAEAQbyFF1G7lt8PLrPSuS8WHHYxxAgfyuJYwG8jQcvUoaP3Mw; prod-edx-language-preference=en; ajs_user_id=8904607; _hjSessionUser_3252782=eyJpZCI6IjFkMDU3M2Y4LTczNGQtNWI3YS05ZDhiLTU2MTg4YjNlMDY1NiIsImNyZWF0ZWQiOjE2NzgxMDI1NDAxMDcsImV4aXN0aW5nIjp0cnVlfQ==; ab.storage.userId.dd7cff88-0bc3-4420-b72b-38f460473479=%7B%22g%22%3A%228904607%22%2C%22c%22%3A1678212540381%2C%22l%22%3A1678212540381%7D; ab.storage.deviceId.dd7cff88-0bc3-4420-b72b-38f460473479=%7B%22g%22%3A%226858f001-4545-1059-288b-f60bfb855b2c%22%2C%22c%22%3A1678212540387%2C%22l%22%3A1678212540387%7D; _hjSession_3252782=eyJpZCI6ImY1MTkzZGFiLTRmZGUtNGNhNy04NmUyLTQxYTU5MGRjYzljMCIsImNyZWF0ZWQiOjE2NzgzMTEyNjA0MzIsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; edx-jwt-cookie-header-payload=eyJhbGciOiJSUzUxMiIsImtpZCI6Imxtc3Byb2QwMDIifQ.eyJhdWQiOiAicmlubXlieWVkbnVhdzVwaGxpZENvY0R1ZGJ5bGJPYkRpYkpvZGJvc2dldHNFYmFsZDQiLCAiZXhwIjogMTY3ODMxODY3NSwgImdyYW50X3R5cGUiOiAicGFzc3dvcmQiLCAiaWF0IjogMTY3ODMxNTA3NSwgImlzcyI6ICJodHRwczovL2NvdXJzZXMuZWR4Lm9yZy9vYXV0aDIiLCAicHJlZmVycmVkX3VzZXJuYW1lIjogIlNwZWVkeVNuYWlsIiwgInNjb3BlcyI6IFsidXNlcl9pZCIsICJlbWFpbCIsICJwcm9maWxlIl0sICJ2ZXJzaW9uIjogIjEuMi4wIiwgInN1YiI6ICIyZWE0MjE4NjA3YjM3ZWNmMGNjNTBiMmU0ODhiNTNjNSIsICJmaWx0ZXJzIjogWyJ1c2VyOm1lIl0sICJpc19yZXN0cmljdGVkIjogZmFsc2UsICJlbWFpbF92ZXJpZmllZCI6IHRydWUsICJ1c2VyX2lkIjogODkwNDYwNywgImVtYWlsIjogImwybG9yZHNAeWFob28uZ3IiLCAibmFtZSI6ICJTcHlyb3MgSy4gTGF6YW5hcyIsICJmYW1pbHlfbmFtZSI6ICJLYXBwYWxhbWRhIiwgImdpdmVuX25hbWUiOiAiU3B5cm9zIiwgImFkbWluaXN0cmF0b3IiOiBmYWxzZSwgInN1cGVydXNlciI6IGZhbHNlfQ; edx-jwt-cookie-signature=kXfu3c5B0d9Nns6xuBh8m_AFU4yVK1lcujXoFTpfGmgLutbo3dYoa2RNRQpP9hO4oEeBpoXgBMUb21biocKdywojBeWrEwhPeFmbxbz2hHZAurnj1DGytm6P47-gQJgIMRnzdXXwKj7-by8YBMzjFDOhwqaMa4nXo7qW_vdDbUpokcPnZpm_StTqyNDHnAnLZIzyZCZyijPm2BqOl0u9mRl-_iKEKv7Frj7zTp81Dv9IYesY_3drZWl9pkMmSwUGblVyhRics4524CZ6GPCt122JCFRc6_xVcRfhY2dr8V4MwoEK3q5oTllWtXfbTcL0TBn4m_p0BSQhKfLamCEeNw; ln_or=eyI1MzMyNjYiOiJkIn0%3D; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Mar+09+2023+01%3A24%3A29+GMT%2B0200+(Eastern+European+Standard+Time)&version=202211.1.0&isIABGlobal=false&hosts=&consentId=724aad42-e256-4eac-a7a7-f02af4750d7f&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=GR%3BI; _hjIncludedInSessionSample_3252782=0; _gat=1; IR_gbd=edx.org; __hstc=23171429.da5e97b673d39d0de95d03f7e9f51741.1678064155376.1678317746079.1678317872121.84; __hssrc=1; AWSELB=D1EF6B6510E347E5B895826CD53CF4FD55E0CFA9A92AE5DB628AA42965D3B1F6484B289FA85D206E0A9AE7B2AC46795D93D381A387583EAE591F65FD084E6693F1009EDC31; AWSELBCORS=D1EF6B6510E347E5B895826CD53CF4FD55E0CFA9A92AE5DB628AA42965D3B1F6484B289FA85D206E0A9AE7B2AC46795D93D381A387583EAE591F65FD084E6693F1009EDC31; lms_sessionid=1|du2iamkvbrkxp6u85mtwa34i2cazip10|6tKD5vBlLyEk|IjU1Y2I3M2EyNDc3YWNjZWU1MGQ3MTk1ZjY3MWY4NjY2YTI2NzhkZGMwMDI2NWMxZDBjZTI3MTU1N2FmZjZmNmMi:1pa39S:M0XQFcyK27oW4TIRHspLxDHAYRM; ab.storage.sessionId.dd7cff88-0bc3-4420-b72b-38f460473479=%7B%22g%22%3A%228ee48d86-7632-a74d-f40e-c019f608053f%22%2C%22e%22%3A1678317925922%2C%22c%22%3A1678317895923%2C%22l%22%3A1678317895923%7D; IR_17728=1678317895989%7C0%7C1678317895989%7C%7C; IR_PI=0764bb90-a028-3a0e-b907-c644e2c34621%7C1678404295989; __hssc=23171429.2.1678317872121"})

        print("SHOW HEADERS", self.client.headers)
        print("SHOW COOKIES", self.client.cookies.get_dict())
        try:
            print("Retrieving courses from Dashboard...Please wait...")
            response = self.client.get(self.urls.DASHBOARD_API_URL)
        except HTTPError as e:
            raise EdxLoginError(f"Login failed. Please check your credentials.Error : {e}")

        except ConnectionError as e:
            raise EdxRequestError(str(e))

        else:
            print(response.json())


            self.scanned = True
            return response.json()


    @is_scanned
    def choose_courses(self ):
        """
        This function is called when the user wants to choose which courses to build.
        """
        if not self.courses_found:
            return []
        choices = []

        # Show dashboard items and multiple choice.
        [print(f"[{i}]  {course[1]}") for i, course in enumerate(self.courses_found)]
        choice = input(
            f"\nType [ALL] to select all courses or type an integer between 0 and {len(self.courses_found) } then  press [Enter] to finalize your choices or [E] to exit: ").strip()
        _user_choices = []
        while True:

            if choice.lower() == 'all':
                _user_choices = self.courses_found
                # self.log('Scraping courses. Please wait..')
                # [course.walk() for course in self.courses]
                break

            if choice.lower() == '':
                if not choices:
                    choice = input(" Select one or more courses, then type [ENTER] to finalize your choices.").strip()
                    continue
                _user_choices = [self.courses_found[i] for i in choices]
                break

            if choice.isdecimal():
                choice = int(choice)
                if choice in choices:
                    choices = input("You have already chosen this course. Try another one")
                choices.append(choice)
                choice = input(f"\nCourse{self.courses_found[choice][0]} is added.\nCurrently selected courses: {choices}\n" + f"Type another one or [ENTER] to finalize your choices: ").strip()
                continue
            if choice.lower() == 'e':
                print("Exiting...")
                sys.exit(0)
            else:
                choice = input(f"Not a valid number. valid input: 1-{len(self.courses_found)}.Retry:").strip()
                continue

        choices = _user_choices
        # TODO USER CHOICES. MAKE TUPLE OF CHOSEN COURSES
        return choices

    @is_scanned
    def inst_courses(self,):
        """
        Choices is a list of integer indexes that
        correspond to each discovered course.
        If no choices are provided, all courses will be parsed.

        """

        [self.courses.append(EdxCourse(self, *c )) for c in self.choose_courses()]
        self.log('Scraping courses. Please wait..')
        [course.walk() for course in self.courses]
    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, value):
        if isinstance(value, list):
            self._courses = value
        else:
            self._courses.append(value)



    def _retrieve_csrf_token(self, ):
        # Retrieve the CSRF token
        try:
            self.client.head(url=self.urls.LOGIN_API_URL,
                            timeout=5)  # sets cookie
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")
        self.urls.csrf_to_headers(self.client)
    @with_driver
    def _ensure_url(self,url,force=True):
        # ensure we are on the dashboard page
        if force and not self.driver.current_url == url:
            self.driver.get(url)
            time.sleep(4)
        return self.driver.current_url == url





    def login_status(self,selenium=True):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        print("Checking if logged in...")

        if selenium:
            return self._status_selenium()
        else:
            return self._status_requests()

    def _status_requests(self,):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        print(self.client.cookies.get('edxloggedin'))
        return self.client.cookies.get('edxloggedin') == 'true'
    @with_driver
    def _status_selenium(self, ):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        self._ensure_url(self.urls.DASHBOARD_URL)
        cookie =self.driver.get_cookie('edxloggedin')
        return cookie and cookie.get('value') == 'true'



    def sign_in(self, selenium=True):
        if selenium:
            return self.sign_in_selenium()
        else:
            return self.sign_in_requests()
    def sign_in_requests(self, ):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        self._retrieve_csrf_token()


        try:
            res = self.client.post(self.urls.LOGIN_API_URL,
                                   data=self.credentials, timeout=20)
            print(res.url)
            print(res.status_code)
            print(res.headers)

            print(res.text)
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        if res.json().get('success', None):
            self.user_auth = True
            print("Logged in")
            return True
        else:
            raise EdxLoginError("Login Failed")
    @with_driver
    def sign_in_selenium(self):

        if not self.login_status(selenium=True):

            if self._ensure_url(self.urls.LOGIN_URL):
                # find email and password fields
                email_elem = WebDriverWait(self.driver,5).until(
                        EC.presence_of_element_located((By.XPATH,'//*[@id="emailOrUsername"]')) )
                password_elem = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="password"]')))

                # fill in
                email_elem.send_keys(self.email)
                password_elem.send_keys(self.password)
                password_elem.send_keys(Keys.RETURN)
                time.sleep(4)
                # # wait for the page to load

                if self.login_status(selenium=True):
                    self.user_auth = True
                    return True
                else:
                    raise EdxLoginError("Login Failed")
        else:
            print("Already logged in")
            return True


