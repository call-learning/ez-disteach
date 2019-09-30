"""
    The base module: defines a base model so we can then use declarative
    syntax for all submodels (a bit like in Django ORM)
"""
import random
import string
from dataclasses import dataclass, field
from typing import List, Type
import importlib

@dataclass
class ModelBase:
    title: str = field(default="")
    items: List[Type["ModelBase"]] = field(default_factory=list)

    """ A root entity class for all ez-disteach (ezdisteach) learning Models"""
    _uid = None
    """ Format availables for input and output """
    _formats = {}
    @property
    def uid(self):
        if self._uid is None:
            self._uid = self._generate_uid()
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    def _generate_uid(self):
        allletters = string.ascii_lowercase
        return ''.join(random.choice(allletters) for i in range(10))

    def load(self, in_stream, format=None, **kwargs):
        """
        Import an entity from a given format from an input stream
        :param in_stream:
        :param format:
        :param kwargs:
        :return:
        """
        module = importlib.import_module(self.__module__)
        if not format:
            format = module.detect_format(in_stream)

        export_book, import_book = self._formats.get(format, (None, None))
        if not import_book:
            raise UnsupportedFormat('Format {0} cannot be loaded.'.format(format))

        module.import_item(self, in_stream, **kwargs)
        return self

    def export(self, format, globalcontext, **kwargs):
        """
        Export the entity to a given format. This will generate a stream which can then be processed
        :param format:
        :param globalcontext: a mutable object shared amongst all entities exported (subentities also)
        :param kwargs: additional args
        :return: a context that can then
        """
        module = importlib.import_module(self.__module__)
        export_item, import_item = self._formats.get(format, (None, None))
        if not export_item:
            raise UnsupportedFormat('Format {0} cannot be exported.'.format(format))

        return module.export_item(self, globalcontext, **kwargs)


def detect_format(stream):
    raise OLAGModelException('Cannot detect format for this module')


def import_item(stream, format=None, **kwargs):
    raise OLAGModelException('Cannot import item for this module')

class OLAGModelException(Exception):
    """ Base class for all exceptions in this module """

    def __init__(self, message):
        self.message = message

class UnsupportedFormat(NotImplementedError):
    "Format is not supported"
