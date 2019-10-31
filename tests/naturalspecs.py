# -*- coding: utf-8 -*-
import unittest

from ezdisteach.lib.naturalspecs.itemparser import get_tokens_from_instruction,replace_quoted_text, get_item_from_instruction

class TestNaturalSpecs(unittest.TestCase):


    def test_replace_quoted_text(self):
        self.assertEqual('Un label nommé ARG_0', replace_quoted_text(INSTRUCTIONS_LABEL[0]))
        self.assertEqual('Une vidéo externe nommée ARG_0 vers ARG_1', replace_quoted_text(INSTRUCTIONS_VIDEO[0]))

    def test_label_tokens(self):
        for i, r in zip(INSTRUCTIONS_LABEL, RESULTS_LABEL):
            item = get_tokens_from_instruction(i, "fr")
            self.assertEqual(r, item)

    def test_link_tokens(self):
        for i, r in zip(INSTRUCTIONS_LINK, RESULTS_LINK):
            item = get_tokens_from_instruction(i, "fr")
            self.assertEqual(r, item)

    def test_video_tokens(self):
        for i, r in zip(INSTRUCTIONS_VIDEO, RESULTS_VIDEO):
            item = get_tokens_from_instruction(i, "fr")
            self.assertEqual(r, item)

    def test_quiz_tokens(self):
        for i, r in zip(INSTRUCTIONS_QUIZ, RESULTS_QUIZ):
            item = get_tokens_from_instruction(i, "fr")
            self.assertEqual(r, item)

    def test_image_tokens(self):
        for i, r in zip(INSTRUCTIONS_IMAGE, RESULTS_IMAGE):
            item = get_tokens_from_instruction(i, "fr")
            self.assertEqual(r, item)


    def test_get_item(self):
        for i, r in zip(INSTRUCTIONS_VIDEO, RESULTS_ITEMS_VIDEO):
            item = get_item_from_instruction(i, "fr")
            self.assertEqual(r, item)

INSTRUCTIONS_LABEL = [
    'Un label nommé "Mon Label"',
]
RESULTS_LABEL = [
    [('NOUN', 'label',''), ('AUX', 'nommé',''), ('PROPN', 'ARG_0','MISC')]
]

INSTRUCTIONS_LINK = [
    'Un lien vers "http://www.wikipedia.org"',
    'Un lien nommé "Wikipedia" vers "http://www.wikipedia.org"',
]

RESULTS_LINK = [
    [('NOUN', 'lien',''), ('PROPN', 'ARG_0','LOC')],
    [('NOUN', 'lien',''), ('AUX', 'nommé',''), ('PROPN', 'ARG_0','MISC'), ('NOUN', 'ARG_1','MISC')]
]

INSTRUCTIONS_VIDEO = [
    'Une vidéo externe nommée "Vidéo d\'exemple" vers "https://www.youtube.com/watch?v=aqz-KE-bpKQhttps://www.youtube.com/watch?v=aqz-KE-bpKQ"',
    'Une vidéo interne nommée "Vidéo interne" du fichier "VIDEO-1.1.mp4"',
]
RESULTS_VIDEO = [
        [('NOUN', 'vidéo',''),('PROPN', 'externe',''),('PROPN', 'nommée',''),('ADJ', 'ARG_0','MISC'), ('NOUN', 'ARG_1','MISC')],
        [('NOUN', 'vidéo',''), ('ADJ', 'interne',''), ('ADJ', 'nommée',''), ('ADJ', 'ARG_0','MISC'), ('NOUN', 'fichier',''), ('NOUN', 'ARG_1','MISC')]
]

RESULTS_ITEMS_VIDEO = [
    ('Video', {'title': "Vidéo d'exemple",'url': 'https://www.youtube.com/watch?v=aqz-KE-bpKQhttps://www.youtube.com/watch?v=aqz-KE-bpKQ'}),
    ('Video', {'title': "Vidéo interne", 'url':'VIDEO-1.1.mp4'}),
]

INSTRUCTIONS_QUIZ = [
    'Un quiz nommé "Quiz 1"',
    'Un quiz nommé "Quiz 1" venant de "quiz.docx"',
]
RESULTS_QUIZ = [
    [('NOUN', 'quiz',''), ('AUX', 'nommé',''), ('PROPN', 'ARG_0','MISC')],
    [('NOUN', 'quiz',''), ('AUX', 'nommé',''), ('PROPN', 'ARG_0','MISC'), ('VERB', 'venant',''),  ('NOUN', 'ARG_1','MISC')]
]

INSTRUCTIONS_IMAGE = [
    'Une image nommée "Image" venant de "NOM DE L\'IMAGE DANS LE SLIDE"'
]
RESULTS_IMAGE = [
    [('NOUN', 'image',''), ('ADJ', 'nommée',''), ('ADJ', 'ARG_0','MISC'), ('VERB', 'venant',''), ('NOUN', 'ARG_1','MISC')]
]
