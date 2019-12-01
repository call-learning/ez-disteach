# -*- coding: utf-8 -*-
"""
    The base module: defines a base model so we can then use declarative
    syntax for all submodels (a bit like in Django ORM)
"""
import importlib
from ezdisteach.lib.tools import generate_uid
from collections.abc import MutableSequence



class Base(MutableSequence):
    """
        A root entity class for all ez-disteach (ezdisteach) learning Models
        We implement the MutableSequence interface so we comply with an usage as a List like item
        to retrieve child items
    """

    _uid = None
    """ Format availables for input and output """
    _formats = {}

    _structure_items = None
    _structure_parent = None

    _meta = None

    MANDATORY_ATTRIBUTES = []
    META_ATTRIBUTES = ['title', 'description']
    STRUCTURAL_ATTRIBUTES = ['items', 'parent']

    def __init__(self, **kwargs):

        self._structure_items = []
        self._meta = {}

        self.__register_formats()

        kwargskeys = kwargs.keys()

        # Check mandatory attributes
        for attrname in self.MANDATORY_ATTRIBUTES:
            if attrname not in kwargskeys:
                raise ModelException(attrname + ' attribute is Mandatory')

        # All other arguments which should be private to the class or a meta attribut
        for key in kwargs:
            setattr(self, key, kwargs[key])  # for items and uid, it is a bit specific and not in the meta

    def load(self, in_stream, format=None, **kwargs):
        """
        Import an entity from a given format from an input stream
        :param in_stream:
        :param format:
        :param kwargs: type of import: import all (including files in a zip file for example) or just the metadata
        :return: self
        """
        module = importlib.import_module('ezdisteach.formats')
        if not format:
            format = module.detect_format(in_stream)

        _, import_stream = self._formats.get(format, (None, None))
        if not import_stream:
            raise UnsupportedFormat('Format {0} cannot be loaded.'.format(format))

        import_stream(self, in_stream, **kwargs)
        return self

    def export(self, format, globalcontext, **kwargs):
        """
        Export the entity to a given format. This will generate a stream which can then be processed
        :param format:
        :param globalcontext: a mutable object shared amongst all entities exported (subentities also)
        :param kwargs: additional args such as "type" which will state what type of export we do (imsmetadata, qti, files...)
        :return: a single stream or a dictionary with filepath <=> output stream.
        """
        module = importlib.import_module(self.__module__)
        export_item, _ = self._formats.get(format, (None, None))
        if not export_item:
            raise UnsupportedFormat('Format {0} cannot be exported.'.format(format))

        return module.export_item(self, globalcontext, **kwargs)

    def __getattr__(self, name):
        # Note that this is only called when the attribute does not exist
        # So we can safely use self.xxx with xx being a property that exists

        if name in self.META_ATTRIBUTES:
            return self._meta.get(name, None)

        if name in self.STRUCTURAL_ATTRIBUTES:
            return getattr(self, '_structure_%s' % name)

        # We must not raise AttributeError in any of the properties
        # https://medium.com/@ceshine/python-debugging-pitfall-mixed-use-of-property-and-getattr-f89e0ede13f1
        raise AttributeNotInMetaInformation(name)

    def __setattr__(self, key, value):
        # Set attr will only be used for Meta attribute as other types of attributes
        # belong to the class (structural attributes that are not created in the class)

        # Native properties first (setattr is called anyway without checks like getattr does)
        if key in dir(self):
            super(Base, self).__setattr__(key, value)
        elif key in self.STRUCTURAL_ATTRIBUTES:
            setattr(self, '_structure_%s' % key, value)
        elif key in self.META_ATTRIBUTES:
            self._meta[key] = value
        else:
            raise AttributeNotInMetaInformation(key)

    @property
    def meta(self):
        """
        :return: a dictionary ??
        """
        # We must not raise AttributeError in this method:
        # https://medium.com/@ceshine/python-debugging-pitfall-mixed-use-of-property-and-getattr-f89e0ede13f1
        return self._meta

    @meta.setter
    def meta(self, value):
        raise Exception('not implemented')

    @property
    def stream(self):
        raise Exception('not implemented')

    @stream.setter
    def stream(self, value):
        self.load(value)

    @property
    def uid(self):
        if self._uid is None:
            self._uid = generate_uid()
        return self._uid

    @classmethod
    def __register_formats(cls):
        """Adds format properties."""
        from ..formats import available as available_formats
        for fmt in available_formats:
            try:
                try:
                    setattr(cls, fmt.title, property(fmt.export_stream, fmt.import_stream))
                    setattr(cls, '%s_meta' % fmt.title, property(fmt.export_meta, fmt.import_meta))
                    setattr(cls, 'get_%s' % fmt.title, fmt.export_stream)
                    setattr(cls, 'set_%s' % fmt.title, fmt.import_stream)
                    setattr(cls, 'get_%s_meta' % fmt.title, fmt.export_meta)
                    setattr(cls, 'set_%s_meta' % fmt.title, fmt.import_meta)

                    cls._formats[fmt.title] = (fmt.export_stream, fmt.import_stream)
                    cls._formats['%s_meta' % fmt.title] = (fmt.export_meta, fmt.import_meta)
                except AttributeError:
                    setattr(cls, fmt.title, property(fmt.export_stream))
                    setattr(cls, 'get_%s' % fmt.title, fmt.export_stream)

                    setattr(cls, '%s_meta' % fmt.title, property(fmt.export_stream))
                    setattr(cls, 'get_%s_meta' % fmt.title, fmt.export_meta)
                    cls._formats[fmt.title] = (fmt.export_stream, None)
                    cls._formats['%s_meta' % fmt.title] = (fmt.export_meta, None)

            except AttributeError:
                cls._formats[fmt.title] = (None, None)

    # List and array like properties of the model (will act on the underliying items list)
    def __getitem__(self, key):
        return self._structure_items[key]

    def __setitem__(self, key, value):
        value._structure_parent = self
        self._structure_items[key] = value

    def __delitem__(self, key):
        if self._structure_items[key]:
            self._structure_items[key]._structure_parent = None
        del self._structure_items[key]

    def __len__(self):
        return len(self._structure_items)

    def insert(self, i, item):
        item._structure_parent = self
        self._structure_items.insert(i, item)


def detect_format(stream):
    raise ModelException('Cannot detect format for this module')


def import_item(stream, format=None, **kwargs):
    raise ModelException('Cannot import item for this module')


def create_model(modelname, **kwargs):
    """"
    :param modelname: is a class name in the model module
    :param kwargs: all other kwargs passed to the init
    :return:
    """
    for subclass in Base.__subclasses__():
        if subclass.__name__ == modelname:
            return subclass(**kwargs)
    raise NoSuchModel(modelname)


class ModelException(Exception):
    """ Base class for all exceptions in this module """

    def __init__(self, message):
        self.message = message


class AttributeNotInMetaInformation(ModelException):
    """Attribute is not in the Meta information of this Model"""

    def __init__(self, attributename):
        self.message = attributename + 'is not in MetaInformation'


class ReadonlyAttribute(ModelException):
    """Attribute is belong to the structure and cannot be set directly"""

    def __init__(self, attributename):
        self.message = attributename + 'belongs to the model internal structure and cannot be set directly'


class NoSuchModel(ModelException):
    """There is no such model"""

    def __init__(self, modelname):
        self.message = modelname + 'is not in MetaInformation'


class UnsupportedFormat(ModelException):
    """Meta attribute not defined"""


class ImportationError(ModelException):
    """Generic error while importing"""

    def __init__(self, importformat, type, specificmessage=None):
        self.message = 'error while importing {} using {} filter'.format(importformat, type)
        if specificmessage:
            self.message += ' :' + specificmessage


