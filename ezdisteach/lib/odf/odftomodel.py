# -*- coding: utf-8 -*-
from odfdo import Document
from .assessmentbuilder import assessment_builder
from .coursebuilder import course_builder
from .sectionbuilder import section_builder

def generic_item_builder(odpdocument, model, **kwargs):
    model.title = kwargs.get('title')
    url = kwargs.get('url', None)
    if url:
        model.url = kwargs.get('url', None)

def video_builder(odpdocument, videomodel, **kwargs):
    generic_item_builder(odpdocument, videomodel, **kwargs)


def link_builder(odpdocument, linkmodel, **kwargs):
    generic_item_builder(odpdocument, linkmodel, **kwargs)

def label_builder(odpdocument, labelmodel, **kwargs):
    generic_item_builder(odpdocument, labelmodel, **kwargs)

def image_builder(odpdocument, labelmodel, **kwargs):
    generic_item_builder(odpdocument, labelmodel, **kwargs)

def build_model(fulldocument: Document, currentmodel, **kwargs):
    modelclassname = currentmodel.__class__.__name__
    builderfunctname = '%s_builder' % modelclassname.lower()
    builderfunct = globals().get(builderfunctname, None)
    if builderfunct:
        return builderfunct(fulldocument, currentmodel, **kwargs)
    else:
        raise NotImplementedError('cannot find builder function {} for {}'.format(builderfunctname, modelclassname))

