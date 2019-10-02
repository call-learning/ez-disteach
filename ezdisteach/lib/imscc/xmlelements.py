# -*- coding: utf-8 -*-
"""
    LXML element specialised for IMSCC purpose
"""
from xml.etree.ElementTree import Element, SubElement

from .tools import get_ressource_path


class IMSRessourceFile(Element):
    def __init__(self, model, type):
        super().__init__('resource')
        self.identifier = ('I_%s' % model.uid).upper()
        self.type = type
        href = get_ressource_path(model)
        SubElement(self, 'file', {'href': href})


class IMSBasicText(Element):
    def __init__(self, tag, text, attributes=None):
        super().__init__(tag)
        self.text = text
        if attributes and isinstance(attributes, dict):
            for key in attributes.keys():
                self.set(key, attributes.get(key))


class IMSItem(Element):
    def __init__(self, model, identifierref=None):
        super().__init__('item')
        self.identifier = ('I_%s' % model.uid).upper()
        if identifierref: self.identifierref = identifierref
        title = IMSBasicText('title', model.title)
        self.append(title)
