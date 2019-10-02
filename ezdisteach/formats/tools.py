# -*- coding: utf-8 -*-

""" EZDisTeach Generic format support
"""


def detect_format(stream):
    """Return format name of given stream."""
    from ezdisteach.formats import available
    for fmt in available:
        try:
            if fmt.detect(stream):
                return fmt.title
        except AttributeError:
            pass
