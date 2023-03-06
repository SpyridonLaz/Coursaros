import sys
import time
from queue import Queue

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


class Edx(BasePlatform, SeleniumSession):
    is_authenticated =BasePlatform.is_authenticated
    _courses =[]
    found = []
    scanned = False
    def __init__(self, email: str, password: str, **kwargs):
        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         **kwargs)

        SeleniumSession.__init__(self ,)
        self.main_tab = self.driver.current_window_handle

    @is_authenticated
    def dashboard_lookup(self):
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
                        self.found.append((slug ,title))

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
        if len(self.found) > 0:
            print("DONE", self.found)
            self.log(f"{len(self.found)} available courses found in your Dashboard!", 'orange')
            return enumerate(self._courses)
        else:
            self.log("No courses available!", "red")


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

    @is_scanned
    def choose_courses(self ):
        """
        This function is called when the user wants to choose which courses to build.
        """
        if not self.found:
            return []
        choices = []

        # Show dashboard items and multiple choice.
        [print(f"[{i}]  {course[1]}") for i, course in enumerate(self.found)]
        choice = input(
            f"\nType [ALL] to select all courses or type an integer between 0 and {len(self.found) } then  press [Enter] to finalize your choices or [E] to exit: ").strip()
        _user_choices = []
        while True:

            if choice.lower() == 'all':
                _user_choices = self.found
                # self.log('Scraping courses. Please wait..')
                # [course.walk() for course in self.courses]
                break

            if choice.lower() == '':
                if not choices:
                    choice = input(" Select one or more courses, then type [ENTER] to finalize your choices.").strip()
                    continue
                _user_choices = [self.found[i] for i in choices]
                break

            if choice.isdecimal():
                choice = int(choice)
                if choice in choices:
                    choices = input("You have already chosen this course. Try another one")
                choices.append(choice)
                choice = input(f"\nCourse{self.found[choice][0]} is added.\nCurrently selected courses: {choices}\n"+f"Type another one or [ENTER] to finalize your choices: ").strip()
                continue
            if choice.lower() == 'e':
                print("Exiting...")
                sys.exit(0)
            else:
                choice = input(f"Not a valid number. valid input: 1-{len(self.found)}.Retry:").strip()

                continue


        choices = _user_choices
        # TODO USER CHOICES. MAKE TUPLE OF CHOSEN COURSES
        return choices

    @is_scanned
    def build_courses(self,):
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

    # def _retrieve_csrf_token(self, ):
    #     # Retrieve the CSRF token
    #     try:
    #         self.client.get(url=self.urls.LOGIN_URL,
    #
    #                         timeout=5)  # sets cookie
    #     except ConnectionError as e:
    #         raise EdxRequestError(f"Error while requesting CSRF token: {e}")
    #     print("CSRF token retrieved")
    #     self.urls.cookie(self.client.cookies)
    #
    # # def sign_in(self):
    # #     # Authenticates the user session. It returns True on success
    # #     # or raises EdxLoginError on failure.
    # #     data = {
    # #         'email': self.email,
    # #         'password': self.password
    # #     }
    # #     self._retrieve_csrf_token()
    # #     try:
    # #         res = self.client.post(self.urls.LOGIN_API_URL, headers=self.urls.headers, data=data,
    # #                                          timeout=20).json()
    # #     except ConnectionError as e:
    # #         raise EdxRequestError(f"Error while requesting Login response:{e}")
    # #     if res.get('success', None):
    # #         self.user_auth = True
    # #         self.save_cookies()
    # #         return True
    # #     else:
    # #         raise EdxLoginError("Login Failed")

    def _ensure_url(self,url):
        # ensure we are on the dashboard page
        if not self.driver.current_url == url:
            self.driver.get(url)
            time.sleep(4)

    def check_if_logged_in(self, cookie=None):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        cookie = cookie or self.driver.get_cookie('edxloggedin')
        cookie = self.client.cookies.get('edxloggedin')
        print("COOKIE", cookie)
        print("Checking if logged in...")
        self._ensure_url(self.urls.DASHBOARD_URL)
        cookie =self.driver.get_cookie('edxloggedin')
        return cookie and cookie.get('value') == 'true'



    def sign_in(self):
        """
        https://authn.edx.org/login
        """
        if not self.check_if_logged_in():

            self._ensure_url(self.urls.LOGIN_URL)
            # find email and password fields
            email_elem = WebDriverWait(self.driver,3).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="emailOrUsername"]')) )
            password_elem = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="password"]')))

            # fill in
            email_elem.send_keys(self.email)
            password_elem.send_keys(self.password)
            password_elem.send_keys(Keys.RETURN)
            time.sleep(4)
            # # wait for the page to load

            if self.check_if_logged_in():
                self.user_auth = True
                return True
            else:
                raise EdxLoginError("Login Failed")
        else:
            print("Already logged in")
            return True






