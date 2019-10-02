"""
    Assessment Model
"""
from ..base import Base


class Assessment(Base):
    MANDATORY_ATTRIBUTES = []
    META_ATTRIBUTES = ['title', 'description']
