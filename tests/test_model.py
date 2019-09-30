import unittest

from olag import Course


class TestModel(unittest.TestCase):

    def test_course_create(self):
        course = Course(languages=['en'],
                        title='Course Title',
                        description='Course Description <span> Span</span>',
                        keywords=['tag1', 'tag2'],
                        items=[])

        self.assertEqual(course.title, "Course Title")

    def test_course_import(self):
        folderimportcourse = Course().load('./cours1/')
        self.assertEqual(folderimportcourse.title, "Mon cours 1")
        zippedimportcourse = Course().load('./cours/cours1.zip')
        self.assertEqual(zippedimportcourse.title, "Mon cours 1")
