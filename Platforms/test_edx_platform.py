import os
import time
from unittest import TestCase
from Platforms.edx_platform import Edx
from dotenv import load_dotenv

load_dotenv()


class TestEdx(TestCase):

    def setUp(self):
        self.email = os.environ.get('EDX_EMAIL')
        self.password = os.environ.get('EDX_PASSWORD')
        self.edx = Edx(self.email, self.password,driver=True)

    def test_edx_urls(self):
        print(self.edx.urls.DASHBOARD_URL)
        print(self.edx.urls.LOGIN_URL)
        print(self.edx.urls.LOGIN_API_URL)
        print(self.edx.urls.PROTOCOL_URL)

    def test_login_status(self,client=None):
        self.assertTrue(self.edx.login_status(client), "User is not logged in")


    def test_get_dashboard(self):

        self.test_sign_in()
        try:

            self.edx.dashboard_lookup()
        except Exception as e:
            self.fail(e)
        # time.sleep(40000)

    def test_build_courses(self):
        self.test_get_dashboard()
        self.edx.inst_courses()

    def test_sign_in(self):
        self.edx.sign_in()
        self.edx.selenium_to_requests(self.edx.client)
        print(self.edx.client.cookies.get('edxloggedin'))
        self.edx.login_status(False)
        self.edx.dashboard_lookup_api(selenium = False)
        time.sleep(22222)

class stand_by:
    def __init__(self):
        self.test = TestEdx()
        self.test.setUp()
        self.edx = self.test.edx
        self.edx.login_status()


class test(stand_by):

    def __init__(self):
        super().__init__()
        self.edx.selenium_to_requests(self.edx.client)



a=test()
q = a.edx

