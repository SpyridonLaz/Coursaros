import time

from Courses.edx_course import EdxCourse
from Platforms.test_edx_platform import TestEdx


class TestEdxCourse(TestEdx):


    def setUp(self):
        print("preparing platform")
        super().setUp()
        self.test_sign_in()

        print("preparing course")
        self.course = EdxCourse(context= self.edx,slug="course-v1:KULeuvenX+WEBSECx+3T2017",title="Introduction to Computer Science and Programming Using Python")



    def test_get_xblocks(self):
        self.course._get_xblocks()

    def test_get_xblocks2(self):
        self.course.slug = "course-v1:MITx+6.00.2x+1T2022"
        self.course._get_xblocks()

        time.sleep(100000)



    def test_walk(self):
        self.course.walk()

