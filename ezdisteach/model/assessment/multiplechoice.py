"""
    Multiple Choice Model
"""
from ..base import Base
from ezdisteach.lib.tools import  generate_uid

class MultipleChoice(Base):
    """
        intro is a text/html text type
        choices is a dictionary of ANSWERID (text) => text/html
        rightanswer is the list of ANSWERID
        feedback is a dictionary of ANSWERID(text) => text/html
        generalfeedback is a generic text for the feedback
    """
    MANDATORY_ATTRIBUTES = ['intro', 'choices', 'rightanswers']
    META_ATTRIBUTES = ['title', 'description', 'intro', 'choices', 'rightanswers', 'feedbacks', 'generalfeedback']

    _choiceuiddict = {}
    def get_choice_uid(self, choiceid):
        currentuid = self._choiceuiddict.get(choiceid, None)
        if currentuid:
            return currentuid
        self._choiceuiddict.set(choiceid, generate_uid())
