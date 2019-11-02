# -*- coding: utf-8 -*-

""" EZDisTeach IMSCC Support
"""

import zipfile
from io import BufferedWriter, StringIO, BytesIO

from yattag import indent

from ezdisteach.lib.imscc.imsccfilebuilder import file_output
from ezdisteach.lib.imscc.imsccmanifestbuilder import get_xml_manifest
from ezdisteach.lib.imscc.imsccqtibuilder import course_xmlqti_builder
from ezdisteach.model.structural import Course

title = 'imscc'
extensions = ('imscc',)

IMSCC_MANIFEST_FILENAME = 'imsmanifest.xml'


def export_stream(model, **kwargs):
    stream = BufferedWriter()
    if not isinstance(model, Course):
        raise NotImplementedError(
            'cannot export anything else than a course model ({} provided)'.format(model.__class__.__name_))

    with zipfile.zipfile(stream) as zfile:
        zfile.write(export_meta(model), IMSCC_MANIFEST_FILENAME)
        file_output(model, zfile)
        qtis = course_xmlqti_builder(model)  # we assume it is a course model
        discussions = course_xmlqti_builder(model)
        stream.seek(0)
    return stream


def import_stream(model, in_stream, **kwargs):
    """Build the model a stream."""
    pass


def import_meta(model, in_stream, **kwargs):
    """Build the model a stream."""
    pass


def export_meta(model, **kwargs):
    """Build the model a stream."""
    metatype = kwargs.get('metatype', None)
    if metatype is None or metatype == 'qti':
        rootdocument = course_xmlqti_builder(model)
    else:
        rootdocument = get_xml_manifest(model)

    xmldocumentcontent = ""
    with BytesIO() as stream:
        rootdocument.write(stream, encoding='utf-8', xml_declaration=True, method='xml')
        xmldocumentcontent = indent(stream.getvalue().decode())
    indentedstream = StringIO()
    indentedstream.write(indent(xmldocumentcontent, indent_text=True))
    return indentedstream


def detect(stream):
    """Returns True if given stream is valid IMS Content Package."""
    try:

        return True
    except (TypeError):
        return False
