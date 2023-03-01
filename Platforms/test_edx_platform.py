from unittest import TestCase

from Platforms.edx_platform import Edx


class TestEdx(TestCase):
    def setUp(self):
        self.email = 'l2lords@yahoo.gr'
        self.password = '4tBGi5pRywuEdtB'
        self.edx = Edx(self.email,self.password)



class TestInit(TestEdx):
    def test_initial_platform(self):

        self.assertEqual( 'Edx' , self.edx.platform,)

class TestSignIn(TestEdx):


    def test_sign_in(self):
        # self.fail()
        self.edx.sign_in()


class TestDashboard(TestSignIn):


    def test_get_dashboard(self):
        if not   self.edx.user_auth:
            print(self.edx.user_auth)
            self.edx.sign_in()
        try:
            self.edx.dashboard_lookup()
        except Exception as e:
            self.fail(e)
