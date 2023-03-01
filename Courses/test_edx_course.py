from unittest import TestCase

from Courses.edx_course import EdxCourse
from Platforms.test_edx_platform import TestEdx, TestSignIn


class TestEdxCourse(TestSignIn):


    def setUp(self):
        print("preparing platform")
        super().setUp()
        self.test_sign_in()

        print("preparing course")
        self.course = EdxCourse(context= self.edx,slug="course-v1:MITx+6.00.2x+1T2022",title="Introduction to Computer Science and Programming Using Python")


    def test_url(self):
        self.fail()

    def test_get_xblocks(self):
        self.course.get_xblocks()