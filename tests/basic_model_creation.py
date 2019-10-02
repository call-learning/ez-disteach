import unittest

from ezdisteach.model import create_model
from ezdisteach.model.file import BinaryFile
from io import IOBase

class TestBasicModelCreation(unittest.TestCase):

    def test_course_create(self):
        course = create_model('Course',
                        languages=['en'],
                        title='Course Title',
                        description='Course Description <span> Span</span>',
                        keywords=['tag1', 'tag2'],
                        items=[])
        self.assertEqual(course.title, 'Course Title')
        self.assertEqual(course.description, 'Course Description <span> Span</span>')

    def test_section_create(self):
            section = create_model('Section',
                            title='Section Title',
                            description = 'Section Description')
            self.assertEqual(section.title, 'Section Title')
            self.assertEqual(section.description, 'Section Description')

    def test_file_create(self):
        with open('./data/ressources/cat.jpg', 'rb') as f:
            file = create_model('BinaryFile', stream=f)
        file.name = 'cat.jpg'
        file.path = '/myressource/'
        self.assertEqual('/myressource/',file.path)
        self.assertEqual('cat.jpg', file.name)
        self.assertTrue(file.stream, IOBase )

    def test_course_create_content_question(self):
        course = create_model('Course',
                       languages=['en'],
                       title='Course Title',
                       description='Course Description <span> Span</span>',
                       keywords=['tag1', 'tag2'])

        file = create_model('BinaryFile')
        with open('./data/ressources/cat.jpg', 'rb') as f:
            file.stream = f

        file.name = 'CatFile.png'
        file.path = '/img/'
        course.append(create_model('Section'))
        course[0].append(file)
        self.assertTrue(isinstance(course[0][0], BinaryFile))

