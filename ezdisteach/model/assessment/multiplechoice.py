"""
    Multiple Choice Model
"""
from ..base import Base


class MultipleChoice(Base):
    MANDATORY_ATTRIBUTES = ['intro', 'choices', 'rightanswers']
    META_ATTRIBUTES = ['title', 'description', 'intro', 'choices', 'rightanswers']
