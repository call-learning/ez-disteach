# -*- coding: utf-8 -*-
import unittest

from odfdo import Document

from ezdisteach.lib.odf import build_model
from ezdisteach.lib.odf.tools import normalize_note_section, parse_note_slide_toml
from ezdisteach.model import create_model


class TestODPCourseImport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        testfiles = ['./data/cours1/plandecours.odp', './data/cours2/plandecours.odp']
        cls._documents = [Document(fpath) for fpath in testfiles]

    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        cls._documents = None

    def test_config_note_parse(self):
        result = parse_note_slide_toml(TEXT_NOTE_QUIZ_SLIDE_TEST_PARSE)
        self.assertEqual(
            ({'quiz': {'quiz1': {'type': 'aiken', 'name': 'Quiz 1'}, 'quiz2': {'type': 'gift', 'name': 'Quiz 2'}}},
             [
                '\nWhat is the correct answer to this question?\nA. Is it this one?\nB. Maybe this answer?\nC. Possibly this one?\nD. Must be this one!\nANSWER: D',
                '\n//Comment line \n::Question title \n:: Question {\n     =A correct answer\n     ~Wrong answer1\n     #A response to wrong answer1\n     ~Wrong answer2\n     #A response to wrong answer2\n     ~Wrong answer3\n     #A response to wrong answer3\n     ~Wrong answer4\n     #A response to wrong answer4\n}']),
            result
        )

    def test_course_simple_odf_import(self):
        course = create_model('Course')
        # First presentation
        build_model(TestODPCourseImport._documents[0], course)
        self.assertEqual("Mon cours 1", course.title)
        self.assertEqual("Description Courte du cours….  Autre description détaillée du cours",
                         course.description.rstrip("\n").rstrip())

    def test_course_ressource_odf_import(self):
        course = create_model('Course')
        # Second presentation
        build_model(TestODPCourseImport._documents[1], course)
        self.assertEqual("Mon cours 1", course.title)
        self.assertEqual("Section 1 /Titre 1", course[0].title)
        self.assertEqual("Section 2/ Titre 2", course[1].title)

    def test_normalize_note_section_zero(self):
        content = normalize_note_section(TEST_NOTE_FIRSTSLIDE_1)
        self.assertEqual(TEST_NOTE_FIRSTSLIDE_1_TARGET, content)

    def test_normalize_note_quiz_section(self):
        content = normalize_note_section(TEST_NOTE_QUIZ_SLIDE_1)
        self.assertEqual(TEST_NOTE_QUIZ_SLIDE_1_TARGET, content)

    def test_ressource_odf_import(self):
        course = create_model('Course')
        section = create_model('Section')
        course.append(section)
        # Second presentation
        build_model(TestODPCourseImport._documents[1], section)
        self.assertEqual("Section 1 / Titre 1", course[0].title)
        self.assertEqual("Section 2 / Titre 2", course[1].title)


TEST_NOTE_FIRSTSLIDE_1 = '''
[Meta]
tags=[ « Tag1 », « Tag2 », « Tag3 »]
Langs= [‘fr’, ‘en’]

[Dates]
Start-date=21-06-2019
End-date=21-07-2019

[misc]
Shortname= « MONCOURS1 »

#(Syntaxe type TOML avec quelques adaptations : pas de sensibilité à la casse et les « » et ‘’ seront normalisés)
'''

TEST_NOTE_FIRSTSLIDE_1_TARGET = '''
[meta]
tags=[ "Tag1", "Tag2", "Tag3"]
langs= ["fr", "en"]

[dates]
start-date=21-06-2019
end-date=21-07-2019

[misc]
shortname= "MONCOURS1"

'''

TEST_NOTE_QUIZ_SLIDE_1 = '''
[quiz]
type = « aiken »
Name = «Quiz 1 » 
---
What is the correct answer to this question?
A. Is it this one?
B. Maybe this answer?
C. Possibly this one?
D. Must be this one!
ANSWER: D
'''

TEST_NOTE_QUIZ_SLIDE_1_TARGET = '''
[quiz]
type = "aiken"
name = "Quiz 1" 
---
What is the correct answer to this question?
A. Is it this one?
B. Maybe this answer?
C. Possibly this one?
D. Must be this one!
ANSWER: D
'''

TEXT_NOTE_QUIZ_SLIDE_TEST_PARSE = '''
[quiz]
[quiz.quiz1]
type = « aiken »
Name = «Quiz 1 » 
[quiz.quiz2]
type = « gift »
Name = «Quiz 2» 
---
What is the correct answer to this question?
A. Is it this one?
B. Maybe this answer?
C. Possibly this one?
D. Must be this one!
ANSWER: D
---
---
//Comment line 
::Question title 
:: Question {
     =A correct answer
     ~Wrong answer1
     #A response to wrong answer1
     ~Wrong answer2
     #A response to wrong answer2
     ~Wrong answer3
     #A response to wrong answer3
     ~Wrong answer4
     #A response to wrong answer4
}
---
'''
