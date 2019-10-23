# -*- coding: utf-8 -*-
import unittest

from ezdisteach.lib.quiztext.aiken import parse_aiken_quiz

class TestAikenParser(unittest.TestCase):

    def test_parse_simple_quiz(self):
        result =  parse_aiken_quiz(SIMPLE_AIKEN)
        resulttext = "\n".join([repr(r) for r in result])
        self.assertEqual(SIMPLE_AIKEN.replace(')','.'), resulttext)

SIMPLE_AIKEN = """What is the correct answer to this question?
A. Is it this one?
B. Maybe this answer?
C. Possibly this one?
D. Must be this one!
ANSWER: D

Which LMS has the most quiz import formats?
A) Moodle
B) ATutor
C) Claroline
D) Blackboard
E) WebCT
F) Ilias
G) edX
ANSWER: A,G
"""
