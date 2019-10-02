# -*- coding: utf-8 -*-
"""
    IMSCC XML XMLBuilder
    Produce an lxml entity ready to convert to text
"""

import xml.etree.ElementTree as ET
from abc import abstractmethod, ABC

from .xmlelements import IMSBasicText, IMSItem, IMSRessourceFile

IMS_VERSION_1 = "1.1.0"

IMSCC_MANIFEST_INFO = {
    IMS_VERSION_1: {
        None: "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1",
        "lomimscc": "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest",
        "lom": "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",

    }
}


class ModelXMLBuilder(ABC):
    def __init__(self, item, rootdocument=None, imsversion=IMS_VERSION_1):
        self.model = item
        self.imsversion = imsversion
        self.rootdocument = rootdocument

    @abstractmethod
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        pass


class CourseXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:

        imsmetaattributes = IMSCC_MANIFEST_INFO.get(self.imsversion, None)

        manifest = ET.Element('manifest')
        self.rootdocument = ET.ElementTree(manifest)

        for mkey, mvalue in imsmetaattributes.items():
            manifest.set('xmlns:%s' % mkey if mkey else 'xmlns', mvalue)
        manifest.set("xsi:schemaLocation", " ".join([val for val in imsmetaattributes.values()]))
        manifest.set('identifier', ('M_%s' % self.model.uid).upper())

        # Add metadata
        metadata = ET.SubElement(manifest, 'metadata')
        metadata.append(IMSBasicText('schema', "IMS Common Cartridge"))
        metadata.append(IMSBasicText('schemaversion', self.imsversion))
        lomgeneral = ET.SubElement(ET.SubElement(metadata, 'lomimscc:lom'), 'lomimscc:general')
        ET.SubElement(lomgeneral, 'lomimscc:title').append(IMSBasicText('lomimscc:string', self.model.title))
        ET.SubElement(lomgeneral, 'lomimscc:description').append(
            IMSBasicText('lomimscc:string', self.model.description))

        for kw in self.model.keywords:
            ET.SubElement(lomgeneral, 'lomimscc:keyword').append(IMSBasicText('lomimscc:string', kw))

        # Add organizations
        rootedorg = ET.SubElement(manifest, 'organization',
                                  {'identifier': ('O_%s' % self.model.uid).upper(), 'structure': 'rooted-hierarchy'})
        ET.SubElement(rootedorg, 'item', {'identifier': 'root'})
        # Add ressources
        ET.SubElement(manifest, 'resources')

        for item in self.model:
            builder = get_xml_builder(item, self.rootdocument)
            builder.build_xml_structure(manifest)  # will build the structure as children of parents


class SectionXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        orgtag = self.rootdocument.getroot().find('organization')
        sectiontag = IMSItem(self.model)
        orgtag.append(sectiontag)

        for item in self.model:
            builder = get_xml_builder(item, self.rootdocument)
            builder.build_xml_structure(sectiontag)


class LabelXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        insertionpoint = self.rootdocument.getroot().find('organization')
        if itemparent:
            insertionpoint = itemparent
        item = IMSItem(self.model)
        insertionpoint.append(item)


class AssessmentXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        insertionpoint = self.rootdocument.getroot().find('organization')
        if itemparent:
            insertionpoint = itemparent
        item = IMSItem(self.model)
        insertionpoint.append(item)
        resources = self.rootdocument.getroot().find('resources')
        ET.SubElement(resources, IMSRessourceFile(self.model,'imsqti_xmlv1p2/imscc_xmlv1p1/assessment'))


class DiscussionXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        insertionpoint = self.rootdocument.getroot().find('organization')
        if itemparent:
            insertionpoint = itemparent
        item = IMSItem(self.model)
        insertionpoint.append(item)

        resources = self.rootdocument.getroot().find('resources')
        ET.SubElement(resources, IMSRessourceFile(self.model,'imsdt_xmlv1p1'))


class BinaryFileXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        insertionpoint = self.rootdocument.getroot().find('organization')
        if itemparent:
            insertionpoint = itemparent
        item = IMSItem(self.model)
        insertionpoint.append(item)

        resources = self.rootdocument.getroot().find('resources')
        ET.SubElement(resources, IMSRessourceFile(self.model,'imsdt_xmlv1p1'))


def get_xml_builder(model, rootdocument=None, imsversion=IMS_VERSION_1):
    modelclassname = model.__class__.__name__
    builderclassname = '%sXMLBuilder' % modelclassname
    builderclass = globals().get(builderclassname, None)
    if builderclass:
        return builderclass(model, rootdocument, imsversion)
    else:
        raise NotImplementedError()
