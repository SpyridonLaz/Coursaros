import sys
from queue import Queue

from requests import HTTPError, exceptions

sys.path.append('..')
import html

from bs4 import BeautifulSoup
from Platforms.platform import BasePlatform

from Courses.edx_course import EdxCourse
from exceptions import EdxRequestError, EdxLoginError
from Urls.edx_urls import EdxUrls


class Edx(BasePlatform, ):
    is_authenticated =BasePlatform.is_authenticated

    def __init__(self, email: str, password: str, **kwargs):
        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         **kwargs)



    @is_authenticated
    def dashboard_urls(self):
        '''
        The main function to scrape the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired, not enrolled or
        unavailable for any reason.

        returns: A list with the URLs of all available courses.
        '''
        print("Retrieving courses from Dashboard...Please wait...")
        try:
            print(self.urls.DASHBOARD_URL)
            response = self.client.get(self.urls.DASHBOARD_URL,timeout=5)
            response.raise_for_status()
        except HTTPError as e:
            raise EdxLoginError(f"Login failed. Please check your credentials.Error : {e}")

        except exceptions.RequestException as e:
            raise EdxLoginError(f"Login failed. Error : {e}")
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        #todo selenium gt egine dynamic
        soup = BeautifulSoup(html.unescape(response.text), 'lxml')
        soup_elem = soup.find_all('a', {'class': ['course-card-title']})
        if soup_elem:

            for i, element in enumerate(soup_elem):
                slug = element.get('data-course-key')

                title = soup.find('h3', {'class': 'course-title',
                                         'id': 'course-title-' + slug}
                                  ).text.strip()

                print (f"[{i}]" ,  title)
                self.courses = EdxCourse(context=self,
                                         slug=slug,
                                         title=title)


        if len(self.courses) > 0:
            # print(available_courses)
            #self.log(f"{len(self.courses)} available courses found in your Dashboard!", 'orange')
            return True
        else:
            #self.log("No courses available!", "red")
            pass


    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, value):
        self._courses.append(value)

    def _retrieve_csrf_token(self, ):
        # Retrieve the CSRF token
        try:
            self.client.get(url=self.urls.LOGIN_URL,

                            timeout=5)  # sets cookie
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")
        print("CSRF token retrieved")
        self.urls.cookie(self.client.cookies)

    def sign_in(self):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        data = {
            'email': self.email,
            'password': self.password
        }
        self._retrieve_csrf_token()
        try:
            res = self.client.post(self.urls.LOGIN_API_URL, headers=self.urls.headers, data=data,
                                             timeout=20).json()
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        if res.get('success', None):
            self.user_auth = True
            self.save_cookies()
            return True
        else:
            raise EdxLoginError("Login Failed")
