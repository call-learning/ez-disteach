# -*- coding: utf-8 -*-

""" EZDisTeach IMSCC Support
"""

import zipfile
from io import BufferedWriter, StringIO, BytesIO

from yattag import indent

from ezdisteach.lib.imscc.imsccxmlbuilder import get_xml_builder
from ezdisteach.lib.imscc.imsccfilebuilder import get_file_output_builder

title = 'imscc'
extensions = ('imscc',)


IMSCC_MANIFEST_FILENAME = 'imsmanifest.xml'

def export_stream(model, **kwargs):
    stream = BufferedWriter()
    with zipfile.zipfile(stream) as zfile:
        zfile.write(export_meta(model), IMSCC_MANIFEST_FILENAME)
        builder = get_file_output_builder(model)
        builder.build_file_structure(zfile)
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
    builder = get_xml_builder(model)
    builder.build_xml_structure(None)
    xmldocumentcontent = ""
    with BytesIO() as stream:
        builder.rootdocument.write(stream, encoding='utf-8', xml_declaration=True, method='xml')
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
