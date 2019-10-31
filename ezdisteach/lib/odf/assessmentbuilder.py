# -*- coding: utf-8 -*-

from ezdisteach.lib.quiztext.aiken import parse_aiken_quiz
from ezdisteach.model import create_model


def assessment_builder(odpdocument, assessmentmodel, **kwargs):
    assessmentmodel.title = kwargs.get('title')
    # Now try to find  the config for this quiz in the note
    quizcontent = ""
    quizformat = ""
    tomlconfig, embedded = kwargs.get('noteparams')
    if tomlconfig.get('quiz'):
        quizindex = 0
        for quizdef in tomlconfig.get('quiz'):
            if tomlconfig['quiz'][quizdef].get('name', None) == kwargs.get('title'):
                quizformat = tomlconfig['quiz'][quizdef].get('type')
                quizcontent = embedded[quizindex]
    if quizcontent and quizformat:
        # TODO manage more formats
        if quizformat == "aiken":
            questions = parse_aiken_quiz(quizcontent + "\n")  # We add an LF so we are sure
            # there is at least one
            items = [
                create_model('MultipleChoice', title=q.intro, intro=q.intro, choices=q.choices,
                             rightanswers=q.rightanswers)
                for q in questions
            ]
            assessmentmodel.extend(items)
