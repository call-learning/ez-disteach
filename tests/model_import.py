import unittest

from ezdisteach.model import create_model


class TestModelImport(unittest.TestCase):

    def test_course_simple_odf_import(self):
        course = create_model('Course')
        with open('./data/cours1/plandecours.odp', 'rb') as f:
            course.load(f, 'odpcourse')
        self.assertEqual("Mon cours 1", course.title)
        self.assertEqual("Description Courte du cours….  Autre description détaillée du cours",
                         course.description.rstrip("\n").rstrip())
        self.assertEqual(['fr', 'en'], course.languages)
        self.assertEqual(['Tag1', 'Tags2', 'Tag 3'], course.keywords)

    def test_course__odf_import(self):
        course = create_model('Course')
        with open('./data/cours2/plandecours.odp', 'rb') as f:
            course.load(f, 'odpcourse')
        self.assertEqual("Mon cours 1", course.title)
        self.assertEqual("Description Courte du cours….  Autre description détaillée du cours",
                         course.description.rstrip("\n").rstrip())
        self.assertEqual("Section 1 / Titre 1", course[0].title)
        self.assertEqual("Section 2 / Titre 2", course[1].title)
