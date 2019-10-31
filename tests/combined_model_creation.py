import unittest

from ezdisteach.model import create_model


class TestCombinedModelCreation(unittest.TestCase):
    _basic_course = None

    def setUp(self):
        self._basic_course = create_model('Course',
                                          languages=['en'],
                                          title='Course Title',
                                          description='Course Description <span> Span</span>',
                                          keywords=['tag1', 'tag2'])

    def test_course_create_with_section(self):
        section1 = create_model('Section',
                                title='Section 1 Title',
                                description='Section 1 Description')

        section2 = create_model('Section',
                                title='Section 2 Title',
                                description='Section 2 Description')
        course = create_model('Course',
                              languages=['en'],
                              title='Course Title',
                              description='Course Description <span> Span</span>',
                              keywords=['tag1', 'tag2'],
                              items=[section1, section2])

        self.assertEqual("Course Title", course.title)
        self.assertEqual("Course Description <span> Span</span>", course.description)
        self.assertEqual("Section 1 Title", course[0].title)
        self.assertEqual("Section 2 Title", course[1].title)

    def test_course_create_content_file(self):
        with open('./data/ressources/cat.jpg', 'rb') as f:
            file = create_model('BinaryFile', stream=f)
            file.name = 'CatFile.png'
            file.path = '/img/'
            self._basic_course.append(create_model('Section'))
            self._basic_course[0].append(file)
            self.assertEqual(self._basic_course[0][0].name, 'CatFile.png')
            file.title = 'Cat Picture'
            self.assertEqual(self._basic_course[0][0].name, 'CatFile.png')

    def test_course_create_content_question(self):
        question1 = create_model('MultipleChoice',
                                 title='Multiple choice 1',
                                 description='Multiple choice description',
                                 intro='Select is the best LMS?',
                                 choices=dict([('A', 'Moodle'), ('B', 'edX'), ('C', 'Other')]),
                                 rightanswers=['A', 'B']
                                 )
        assessment = create_model('Assessment',
                                  title='Assessment',
                                  items=[question1])
        self._basic_course.append(create_model('Section'))
        self._basic_course[0].append(assessment)
