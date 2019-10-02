# -*- coding: utf-8 -*-
"""
    IMSCC XML XMLBuilder
    Tools
"""
from ezdisteach.model.base import Base as BaseModel

_class_list = None


def get_model_class_list():
    global _class_list
    if _class_list is not None:
        return _class_list
    _class_list = [cls.__name__ for cls in BaseModel.__subclasses__()]
    return _class_list



