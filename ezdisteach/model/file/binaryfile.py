"""
    BinaryFile Model
"""
import tempfile

from ..base import Base


class BinaryFile(Base):
    MANDATORY_ATTRIBUTES = []
    META_ATTRIBUTES = ['title', 'name', 'path']

    _current_file = None

    def load(self, in_stream, format=None, **kwargs):
        """
        Load a binary file. No conversion
        """
        # Delete previous file
        if self._current_file is not None:
            self._current_file.close()

        self._current_file = tempfile.SpooledTemporaryFile()
        in_stream.seek(0)
        self._current_file.write(in_stream.read())

    # Ignore format, just output a stream
    def export(self, format, globalcontext, **kwargs):
        if self._current_file is not None:
            self._current_file.seek(0)
        return self._current_file

    @property
    def stream(self):
        return self.export(None, None)

    @stream.setter
    def stream(self, value):
        self.load(value)


    def __delete__(self, instance):
        if self._current_file is not None:
            self._current_file.close()
