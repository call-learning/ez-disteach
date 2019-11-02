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

def course_xmlmanifest_builder(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                       imsversion=IMS_VERSION_1):
    imsmetaattributes = IMSCC_MANIFEST_INFO.get(imsversion, None)

    manifest = ET.Element('manifest')
    rootdocument = ET.ElementTree(manifest)

    for mkey, mvalue in imsmetaattributes.items():
        manifest.set('xmlns:%s' % mkey if mkey else 'xmlns', mvalue)
    manifest.set("xsi:schemaLocation", " ".join([val for val in imsmetaattributes.values()]))
    manifest.set('identifier', ('M_%s' % model.uid).upper())

    # Add metadata
    metadata = ET.SubElement(manifest, 'metadata')
    metadata.append(IMSBasicText('schema', "IMS Common Cartridge"))
    metadata.append(IMSBasicText('schemaversion', imsversion))
    lomgeneral = ET.SubElement(ET.SubElement(metadata, 'lomimscc:lom'), 'lomimscc:general')
    ET.SubElement(lomgeneral, 'lomimscc:title').append(IMSBasicText('lomimscc:string', model.title))
    ET.SubElement(lomgeneral, 'lomimscc:description').append(
        IMSBasicText('lomimscc:string', model.description))

    for kw in model.keywords:
        ET.SubElement(lomgeneral, 'lomimscc:keyword').append(IMSBasicText('lomimscc:string', kw))

    # Add organizations
    rootedorg = ET.SubElement(manifest, 'organization',
                              {'identifier': ('O_%s' % model.uid).upper(), 'structure': 'rooted-hierarchy'})
    ET.SubElement(rootedorg, 'item', {'identifier': 'root'})
    # Add ressources
    ET.SubElement(manifest, 'resources')

    for item in model:
        get_xml_manifest(item, rootdocument, itemparent, imsversion)
    return rootdocument


def section_xmlmanifest_builder(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                        imsversion=IMS_VERSION_1):
    orgtag = rootdocument.getroot().find('organization')
    sectiontag = IMSItem(model)
    orgtag.append(sectiontag)

    for item in model:
        get_xml_manifest(item, rootdocument, sectiontag)
    return sectiontag


def label_xmlmanifest_builder(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                      imsversion=IMS_VERSION_1):
    insertionpoint = rootdocument.getroot().find('organization')
    if itemparent:
        insertionpoint = itemparent
    item = IMSItem(model)
    insertionpoint.append(item)
    return item


def assessment_xmlmanifest_builder(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                           imsversion=IMS_VERSION_1):
    insertionpoint = rootdocument.getroot().find('organization')
    if itemparent:
        insertionpoint = itemparent
    item = IMSItem(model)
    insertionpoint.append(item)
    resources = rootdocument.getroot().find('resources')
    ET.SubElement(resources, IMSRessourceFile(model, 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment'))
    return item


def discussion_xmlmanifest_builder(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                           imsversion=IMS_VERSION_1):
    insertionpoint = rootdocument.getroot().find('organization')
    if itemparent:
        insertionpoint = itemparent
    item = IMSItem(model)
    insertionpoint.append(item)
    resources = rootdocument.getroot().find('resources')
    ET.SubElement(resources, IMSRessourceFile(model, 'imsdt_xmlv1p1'))
    return item


def get_xml_manifest(model, rootdocument: ET.ElementTree = None, itemparent: ET.Element = None,
                      imsversion=IMS_VERSION_1):
    modelclassname = model.__class__.__name__
    builderfunctname = '%s_xmlmanifest_builder' % modelclassname.lower()
    builderfunct = globals().get(builderfunctname, None)
    if builderfunct:
        return builderfunct(model, rootdocument, itemparent, imsversion)
    else:
        raise NotImplementedError('cannot find xml builder function {} for {}'.format(builderfunctname, modelclassname))
