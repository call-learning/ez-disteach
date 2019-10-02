"""
    Course Model
"""
from ..base import Base


class Course(Base):
    MANDATORY_ATTRIBUTES = []
    META_ATTRIBUTES = ['title', 'description', 'languages', 'keywords']
