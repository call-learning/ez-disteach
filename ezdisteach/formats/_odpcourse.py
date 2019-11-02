# -*- coding: utf-8 -*-

""" EZDisTeach ODP Course format support
"""

from io import BufferedWriter
import zipfile
import tempfile
from odfdo import Document

title = 'odpcourse'
extensions = ('odp',)


def export_stream(model, **kwargs):
    pass

def import_stream(model, in_stream, **kwargs):
    from ezdisteach.lib.odf.odftomodel import build_model
    # Here we receive a stream and th  odf lib uses only files
    # So we need to convert the stream to a temporary file
    with  tempfile.NamedTemporaryFile() as f:
        f.write(in_stream.read())
        document = Document(f)
        build_model(document, model)


def import_meta(model, in_stream, **kwargs):
    """Build the model a stream."""
    import_stream(model, in_stream, type="meta")
    pass

def export_meta(model, **kwargs):
    """Build the model a stream."""
    export_stream(model, type="meta")
    pass


def detect(stream):
    """Returns True if given stream is valid IMS Content Package."""
    try:

        return True
    except (TypeError):
        return False
