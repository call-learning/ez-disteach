# -*- coding: utf-8 -*-

from itertools import chain

from lark import Lark, Transformer

aiken_grammar = '''
    %import common.NEWLINE
    %import common.CR
    %import common.LF
    %import common.WS_INLINE
    %import common.UCASE_LETTER
    
    ANSWERNUMBER: /[A-Z][\.)]/
    ANSWERKW: "ANSWER:"
    SINGLENEWLINE: WS_INLINE? CR? LF 
    SENTENCE: /(\S|[ \t\f\v])+/ SINGLENEWLINE

    
    quiz: SINGLENEWLINE* _questions SINGLENEWLINE*
    
    _questions: question 
            | _questions SINGLENEWLINE question
    
    question: intro choices rightanswers
    
    intro: SENTENCE
    
    choices: choice 
        | choices choice
    
    choice: ANSWERNUMBER WS_INLINE SENTENCE
    
    rightanswers: ANSWERKW  WS_INLINE _answerslist SINGLENEWLINE
    
    _answerslist: singleanswer 
        | _answerslist "," singleanswer
    
    singleanswer: WS_INLINE? UCASE_LETTER WS_INLINE? 
'''


class AikenTreeTransformer(Transformer):
    def rightanswers(self):
        return [a for a in self if type(a) is str]

    def singleanswer(self):
        return self[0].value

    def intro(self):
        return self[0].value.strip("\n")

    def choice(self):
        answer = self[0].value[:-1]
        value = self[1].value.strip("\n") if self[1].type == 'SENTENCE' else self[2].value.strip("\n")
        return (answer, value)

    def choices(self):
        return self if type(self[0]) is tuple else list(chain.from_iterable([self[0], [self[1]]]))

    def question(self):
        question = AikenQuestion(self[0], self[1], self[2])
        return question

    def quiz(self):
        return [q for q in self if isinstance(q, AikenQuestion)]


akien_parser = Lark(aiken_grammar, parser='lalr', start='quiz', debug=False, transformer=AikenTreeTransformer)


def parse_aiken_quiz(aikenquiztxt):
    result = akien_parser.parse(aikenquiztxt)
    return result


class AikenQuestion:
    intro = ""
    choices = {}
    rightanswers = []

    def __init__(self, intro, choices, rightanswers):
        self.intro = intro
        self.choices = dict(choices)
        self.rightanswers = rightanswers

    def __repr__(self):
        text = self.intro + "\n"
        text = text + "\n".join([k + ". " + v for k, v in self.choices.items()]) + "\n"
        text = text + "ANSWER: " + ",".join(self.rightanswers) + "\n"
        return text
