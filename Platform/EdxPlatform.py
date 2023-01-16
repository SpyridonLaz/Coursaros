import html
from pathlib import Path

import validators
from bs4 import BeautifulSoup

from Exceptions import EdxRequestError, EdxLoginError
from .Platform import AbstractPlatform
from Urls.EdxUrls import EdxUrls

class Edx(AbstractPlatform,EdxUrls):


    def __init__(self, email, password,SAVE_TO:Path= Path.home() ):

        super(AbstractPlatform).__init__(email=email,
                         password=password,
                         platform='edx',
                         HOSTNAME=self.HOSTNAME,
                         SAVE_TO=SAVE_TO)

    def dashboard_urls(self):
        '''
        The main function to scrape the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired, not enrolled or
        unavailable for any reason.

        returns: A list with the URLs of all available courses.
        '''

        self.available_courses = []
        try:
            response = self.client.get(self.DASHBOARD_URL)
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        soup = BeautifulSoup(html.unescape(response.text), 'lxml')
        soup_elem = soup.find_all('a', {'class': 'course-target-link enter-course'})
        if soup_elem:
            for i, element in enumerate(soup_elem):
                course_slug = element.get('data-course-key')

                course_title = soup.find('h3', {'class': 'course-title',
                                                'id': 'course-title-' + course_slug}
                                         )
                print(course_title)
                course_title = course_title.text.strip()

                course_url = "{}/{}/".format(self.COURSE_BASE_URL, course_slug)
                self.available_courses.append({'course_dir': course_title,
                                          'course_url': course_url,
                                          'course_slug': course_slug}
                                         )
                self.available_courses.append(course_url) if validators.url(course_url) else None
        print(self.available_courses)
        return self.available_courses


    def _retrieve_csrf_token(self):
        # Retrieve the CSRF token first
        try:
            self.client.get(self.LOGIN_URL, timeout=20)  # sets cookie

            if 'csrftoken' in self.client.cookies:
                # Django 1.6 and up
                csrftoken = self.client.cookies.get('csrftoken',None)
                print(csrftoken)
            else:
                # older versions
                csrftoken = self.client.cookies.get('csrf',None)

        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")

        self._headers['x-csrftoken'] = csrftoken



    def sign_in(self):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        self._retrieve_csrf_token()
        data = {
            'email': self.email,
            'password': self.password
        }
        try:
            res = self.client.post(self.LOGIN_API_URL, headers=self.headers, data=data, timeout=10).json()
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        if res.get('success') is True:
            self.is_authenticated = True
            return True
        else:
            raise EdxLoginError("Login Failed")


