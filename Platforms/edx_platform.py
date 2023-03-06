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

    def __init__(self, email: str, password: str, **kwargs):
        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         **kwargs)

        SeleniumSession.__init__(self , self.client)
        self.main_tab = self.driver.current_window_handle
        self. courses = []
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

            self._dash_nav(self.urls.DASHBOARD_URL)
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
                is_active = course_card.find_element(By.CLASS_NAME,"btn.btn-primary").is_enabled()

                if is_active:
                    _elem = course_card.find_element(By.CLASS_NAME, 'course-card-title')
                    title = _elem.text
                    # startswith('course-v1')
                    _split= [   x for x in _elem.get_attribute('href').split('/') if x.startswith('course-v1')]
                    try:
                        slug = _split[-1]
                    except IndexError:
                        print("INDEX ERROR  - DASHBOARD URLS")
                        continue

                    print (is_active,title, slug)
                    self.courses = self,slug, title


            time.sleep(400000)
            try:
                next_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,'//button[(contains(@class,"btn-icon"))  and (contains(@class,"next")) and (not (@disabled))]'))   )
            except TimeoutException:
                print("No more pages")

                break
            else:

                next_btn.send_keys(Keys.RETURN)
                time.sleep(2)

        if len(self.courses) > 0:
            print(self.courses)
            self.log(f"{len(self.courses)} available courses found in your Dashboard!", 'orange')
            return True
        else:
            self.log("No courses available!", "red")
            pass
        return self.courses

    def choose_courses(self ):
        choices = None
        # TODO USER CHOICES
        return self.build_courses(choices=choices)


    def build_courses(self, choices:list =None):
        #choices is a list of integer indexes that
        # correspond to each discovered course.
        choices =  choices or range(len(self.courses))
        return [ EdxCourse(*course) for i, course in enumerate(self.courses) if i in choices]

    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, value):
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

    def _dash_nav(self,url):
        if not self.driver.current_url == url:
            self.driver.get(url)
            time.sleep(4)

    def check_if_logged_in(self):
        # Checks if the user is logged in by checking the cookies.
        # It returns True if the user is logged in or False otherwise.
        print("Checking if logged in...")
        self._dash_nav(self.urls.DASHBOARD_URL)
        cookie =self.driver.get_cookie('edxloggedin')
        return cookie and cookie.get('value') == 'true'



    def sign_in(self):
        """
        https://authn.edx.org/login
        """
        if not self.check_if_logged_in():

            self._dash_nav(self.urls.LOGIN_URL)
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



