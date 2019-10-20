# -*- coding: utf-8 -*-
"""
    IMSCC File Builder
    Produce an lxml entity ready to convert to text
"""

from abc import abstractmethod, ABC

from lxml import etree
from lxml.etree import ElementBase

from .xmlelements import IMSBasicText, IMSItem, IMSRessourceFile
import io
class ModelFileOutputBuilder:
    def __init__(self, item, ioopen = io.open):
        self.model = item
        self.openfile = ioopen

    def output_file(self, basepath) -> None:
        pass


class CourseFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        for item in self.model:
            get_file_output_builder(item, self.openfile)


class SectionFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        for item in self.model:
            get_file_output_builder(item, self.openfile)

class LabelFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        pass

class AssessmentFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:

        pass

class DiscussionFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        # Output the discussion.xml file
        pass


class BinaryFileFileOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        with self.openfile(self.model.name, 'w') as f:
            f.write(self.model.export())


class ImageOutputBuilder(ModelFileOutputBuilder):
    def output_file(self, basepath) -> None:
        with self.openfile(self.model.name, 'w') as f:
            f.write(self.model.export())




def get_file_output_builder(model, ioopen = io.open):
    modelclassname = model.__class__.__name__
    builderclassname = '%sFileOutputBuilder' % modelclassname
    builderclass = globals().get(builderclassname, None)
    if builderclass:
        return builderclass(model, ioopen)
    else:
        raise NotImplementedError()
