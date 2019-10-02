# -*- coding: utf-8 -*-

""" EZDisTeach formats
"""

from . import _odpcourse as odpcourse
from . import _imscc as imscc
from .tools import detect_format

available = (imscc, odpcourse)
