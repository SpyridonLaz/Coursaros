import sys
import time
from json import JSONDecodeError

from requests import HTTPError, exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append('../..')

from coursaros.base.platform import BasePlatform

from coursaros.edx.course import EdxCourse
from coursaros.edx.exceptions import EdxRequestError, EdxLoginError
from coursaros.edx.urls import EdxUrls


class Edx(BasePlatform,):
    _courses =[]
    courses_found = []
    scanned = False
    def __init__(self, email: str, password: str, *args , **kwargs):

        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         *args ,**kwargs)


        self.requests_auth = None
        self.selenium_auth = None


    @staticmethod
    def logged_in(selenium):
        """ Decorator to check if the user is logged in """

        def wrapper(func):
            def nested_wrapper(self, *args, **kwargs):

                if selenium:
                    if self.selenium_auth or self._status_selenium():
                        self.selenium_auth = True
                        return func(self, *args, **kwargs)
                else:
                    if self.requests_auth or self._status_requests():
                        self.requests_auth = True
                        return func(self, *args, **kwargs)

                print("Not logged in.")

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
        Function to scrape the dashboard for all available courses
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
        courses_found = []
        while True:
            course_cards = self.driver.find_elements(By.CLASS_NAME, 'course-card')
            print(len(course_cards))
            for course_card in course_cards:
                slug , title = None, None
                # time.sleep(0.1)
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
                        continue

                    print (title, slug)
                    if slug and title :
                        courses_found.append((slug , title))

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
        return self.check_results(courses_found)

    def create_course(self, slug, title):
        self.courses = EdxCourse(context=self, slug=slug, title=title)
        return

    def check_results(self,courses_found):

        if len(courses_found) > 0:
            self.courses_found = courses_found
            self.log(f"{len(self.courses_found)} available courses found in your Dashboard!", 'orange')
            return self._courses
        else:
            self.log("No courses available!", "red")


    @logged_in(selenium=False)
    def dashboard_lookup_api(self, *args, **kwargs):
        """ dashboard lookup using the edx api """
        self._retrieve_csrf_token(self.urls.API_DOCS_URL)
        courses_found = []
        try:
            print("\nRetrieving courses from Dashboard...Please wait...")
            response = self.client.get(self.urls.DASHBOARD_API_URL)
            # print("REQUEST COOKIE HEADER", repr(response.request.headers['Cookie']))
            self.response = response
            res_json = response.json()
            response.raise_for_status()
        except HTTPError as e:
            raise EdxLoginError(f"Login failed. Please check your credentials.Error : {e}")
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        except JSONDecodeError as e:
            raise EdxRequestError(f"Failed to decode JSON response. Error : {e}")
        
        else:
            courses_found += [   (v['course_name'],v['course_id'])   for i in res_json for k,v in i.items() if k=='course_details' and isinstance(i,dict)]

            self.scanned = True
            return self.check_results(courses_found)

    @is_scanned
    def choose_courses(self ) ->list[tuple[str,str]]:
        """
        This function is called when the user wants to choose which courses to build.
        Choices is a list of integer indexes that
        correspond to each discovered course.
        If no choices are provided, all courses will be parsed."""
        if not self.courses_found:
            return []
        choices = []

        # Show dashboard items and multiple choice.
        [print(f"[{i}]  {course[1]}") for i, course in enumerate(self.courses_found)]
        _prompt_msg = f"\nType [ALL] to select all courses or type an integer between 0 and {len(self.courses_found) } then  press [Enter] to finalize your choices or [E] to exit: ".strip()


        choice = input(_prompt_msg).strip()
        _user_choices = []
        while True:
            if choice.lower() == 'all':
                return self.courses_found
            elif choice.lower() == '':
                if not choices:
                    choice = input(_prompt_msg).strip()
                    continue
                return [self.courses_found[i] for i in choices]

            elif choice.isdecimal():
                choice = int(choice)
                if choice in choices:
                    choices = input("You have already chosen this course. Try another one")
                choices.append(choice)
                choice = input(f"\nCourse{self.courses_found[choice][0]} is added.\nCurrently selected courses: {choices}\n" + f"Type another one or [ENTER] to finalize your choices: ").strip()
                continue
            elif choice.lower() == 'e':
                print("Exiting...")
                sys.exit(0)
            else:
                choice = input(f"Valid input: 0-{len(self.courses_found)}. \nRetry:").strip()
                continue




    @is_scanned
    def inst_courses(self,):
        [self.courses.append(EdxCourse(self, *c )) for c in self.choose_courses()]
        self.log('Scraping courses. Please wait..')
        [course.walk() for course in self.courses]
    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, tuple):
        self._courses.append(EdxCourse(*tuple))



    def _retrieve_csrf_token(self, url):
        # Retrieve the CSRF token
        try:
            self.client.get(url= url,
                            timeout=5)  # sets cookie
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")
        self.urls.csrf_to_headers(self.client)


    def status(self,selenium=True):
        print("Checking status...")
        msg= "logged in with {}"

        if selenium:
            if self.selenium_auth or self._status_selenium():
                self.selenium_auth = True
                print(msg.format("selenium."))

                return True
        else:
            if self.requests_auth or self._status_requests():
                self.requests_auth = True
                print(msg.format("requests."))

                return True
        print("Not logged in.")
        return False


    def _status_requests(self,):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        return self.client.cookies.get('edxloggedin') == 'true'

    @with_driver
    def _status_selenium(self, ):
        # Checks if the user is logged in by checking edxloggedin cookie.
        # It returns True if the user is logged in or False otherwise.
        self._ensure_url(self.urls.DASHBOARD_URL)
        cookie =self.driver.get_cookie('edxloggedin')

        return cookie and cookie.get('value') == 'true'



    def login(self, selenium=True):
        if selenium:
            return self.sign_in_selenium()
        else:
            return self.sign_in_requests()
    def sign_in_requests(self, ):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        self._retrieve_csrf_token(self.urls.LOGIN_URL)

        try:
            res = self.client.post(self.urls.LOGIN_API_URL,
                                   data=self.credentials, timeout=20)
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        except JSONDecodeError as e:
            raise EdxRequestError(f"Error while decoding Login response:{e}")
        if res.text and res.json().get('success', None):
            self.selenium_auth = True
            print("Login Successful")
            return True
        else:
            print(res.text)

    @with_driver
    def _ensure_url(self,url,force=True):
        # ensure we are on the dashboard page
        if force and not self.driver.current_url == url:
            self.driver.get(url)
            time.sleep(4)
        return self.driver.current_url == url



    @with_driver
    def sign_in_selenium(self):
        if not self.status(selenium=True):
            print("Signing in...")
            if self._ensure_url(self.urls.AUTH_LOGIN_URL):
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

                if self.status(selenium=True):
                    print("Login Successful")
                    self.selenium_auth = True
                    return True

        else:
            print("Already logged in")
            return True


