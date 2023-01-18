import html
from pathlib import Path
import lxml
import validators
from bs4 import BeautifulSoup

from Courses.EdxCourse import EdxCourse
from Exceptions import EdxRequestError, EdxLoginError
from Platforms.Platform import BasePlatform, SessionManager
from Urls.EdxUrls import EdxUrls


class Edx(BasePlatform, ):
    authenticated = SessionManager.is_authenticated

    def __init__(self, email: str, password: str, **kwargs):

        super().__init__(email=email,
                         password=password,
                         urls=EdxUrls(),
                         **kwargs)
        self._courses = []

    @authenticated
    def dashboard_urls(self):
        '''
        The main function to scrape the main dashboard for all available courses
        including archived.
        It does NOT parse courses whose access has expired, not enrolled or
        unavailable for any reason.

        returns: A list with the URLs of all available courses.
        '''
        print("entered dash")
        try:
            response = self.connector.client.get(self.urls.DASHBOARD_URL)
        except ConnectionError as e:
            raise EdxRequestError(str(e))

        soup = BeautifulSoup(html.unescape(response.text), 'lxml')
        soup_elem = soup.find_all('a', {'class': ['enter-course']})
        if soup_elem:
            for i, element in enumerate(soup_elem):
                print("found dash")

                slug = element.get('data-course-key')

                title = soup.find('h3', {'class': 'course-title',
                                         'id': 'course-title-' + slug}
                                  ).text.strip()

                self.courses = (title,
                                {i:EdxCourse(context=self,
                                         slug=slug,
                                         title=title)}
                          )

        print("exit dash")

        print(self.courses)

    @property
    def courses(self):
        return self._courses

    @courses.setter
    def courses(self, value):
        self._courses += [value]

    def _retrieve_csrf_token(self, ):
        # Retrieve the CSRF token
        try:
            self.connector.client.get(self.urls.LOGIN_URL, timeout=20)  # sets cookie
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting CSRF token: {e}")
        self.urls.cookie(self.connector.client.cookies)

    def sign_in(self):
        # Authenticates the user session. It returns True on success
        # or raises EdxLoginError on failure.
        data = {
            'email': self.email,
            'password': self.password
        }
        self._retrieve_csrf_token()
        try:
            res = self.connector.client.post(self.urls.LOGIN_API_URL, headers=self.urls.headers, data=data,
                                             timeout=10).json()
        except ConnectionError as e:
            raise EdxRequestError(f"Error while requesting Login response:{e}")
        if res.get('success', None) is True:
            self.is_authenticated = True
            self.connector.save_cookies()
            return True
        else:
            raise EdxLoginError("Login Failed")
