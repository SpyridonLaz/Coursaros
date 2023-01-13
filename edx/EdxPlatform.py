from Platform.Platform import *


class Edx(Platform):


    def __init__(self, email, password, platform='edx'):
        # Creates a request session
        super().__init__(email, password, platform)
        self.client = requests.Session()
        # The EDX account's email
        self.email = email
        self.collector = ItemCollector.Collector(BASE_FILEPATH=self.BASE_FILEPATH)

        self.session_file_exists = Path(self.SAVED_SESSION_PATH).exists()
        # Cookie location
        # These headers are required. Some may not be required
        # but sending all is a good practice.


        # This is set True later and is used to
        # avoid unnecessary login attempts
        self.is_authenticated = False



    def headers(self):
        # Generate a fake user-agent to avoid 403 error
        self._headers['user-agent'] = UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome


        return self._headers


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


