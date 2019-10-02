import xml.etree.ElementTree as ET
from .imsccxmlbuilder import ModelXMLBuilder


IMS_QTI_VERSION_1 = "1.2"
IMSCC_QTI_MANIFEST_INFO = {
    IMS_QTI_VERSION_1: {
        None: "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instancet",
    }
}

class AssessmentXMLBuilder(ModelXMLBuilder):
    def build_xml_structure(self, itemparent: ET.Element = None) -> None:
        imsmetaattributes = IMSCC_QTI_MANIFEST_INFO.get(self.imsversion, None)

        questestinterop = ET.Element('questestinterop')
        self.rootdocument = ET.ElementTree(questestinterop)

        for mkey, mvalue in imsmetaattributes.items():
            questestinterop.set('xmlns:%s' % mkey if mkey else 'xmlns', mvalue)
        questestinterop.set("xsi:schemaLocation", " ".join([val for val in imsmetaattributes.values()]))
        assessment = ET.SubElement(questestinterop, 'questestinterop')
        assessment.set('ident', ('QBD_%s' % self.model.uid).upper())
        assessment.set('title', 'QBD_%s' % self.model.test)

        qtimetadata = ET.SubElement(assessment, 'qtimetadata')

        # TODO see if that can be taken from the model
        FIELD_ENTRY = [('cc_profile', 'cc.exam.v0p1'), ('qmd_assessmenttype', 'Examination')]
        for fe in FIELD_ENTRY:
            qtimetadatafield = ET.SubElement(qtimetadata, 'qtimetadatafield')
            fieldlabel = ET.SubElement(qtimetadatafield, 'fieldlabel')
            fieldentry = ET.SubElement(qtimetadatafield, 'fieldentry')
            fieldlabel.set_text(fe[0])
            fieldentry.set_text(fe[1])

        rubric = ET.SubElement(assessment, 'rubric')
        material = ET.SubElement(rubric, 'material')
        material.set('label','Summary')  # TODO there should be some language dependent string here
        mattext = ET.SubElement(material, 'mattext')
        mattext.set_text('<![CDATA[%s]]'%self.model.title)

        section = ET.SubElement(assessment, 'section')
        assessment.set('ident', ('I_%s' % self.model.uid).upper())
        # Now we add each assesment items (questions)


def get_xml_builder(model, rootdocument=None, imsversion=IMS_VERSION_1):
    modelclassname = model.__class__.__name__
    builderclassname = '%sXMLBuilder' % modelclassname
    builderclass = globals().get(builderclassname, None)
    if builderclass:
        return builderclass(model, rootdocument, imsversion)
    else:
        raise NotImplementedError()
