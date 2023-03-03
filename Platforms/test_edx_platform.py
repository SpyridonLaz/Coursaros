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
        self.edx = Edx(self.email, self.password)

    def test_edx_urls(self):
        print(self.edx.urls.DASHBOARD_URL)
        print(self.edx.urls.LOGIN_URL)
        print(self.edx.urls.PROTOCOL_URL)

    def test_check_if_logged_in(self):
        self.assertTrue(self.edx.check_if_logged_in() , "User is not logged in")

    def test_sign_in(self):
        # self.fail()
        self.edx.sign_in()

    def test_get_dashboard(self):

        self.test_sign_in()
        try:

                self.edx.dashboard_lookup()
        except Exception as e:
            self.fail(e)
        time.sleep(40000)



class stand_by:
    def __init__(self):
        self.test = TestEdx()
        self.test.setUp()

        self.test.edx.sign_in()

