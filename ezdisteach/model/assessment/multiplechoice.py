"""
    Multiple Choice Model
"""
from ..base import Base


class MultipleChoice(Base):
    MANDATORY_ATTRIBUTES = []
    META_ATTRIBUTES = ['title', 'description', 'rightchoices', 'questions']
