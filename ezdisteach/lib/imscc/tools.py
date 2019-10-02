# -*- coding: utf-8 -*-
"""
    IMSCC XML XMLBuilder
    Tools
"""

def get_assessment_path(model):
    return ('I_%s/assessment.xml' % model.uid).lower()

def get_discussion_path(model):
    return ('I_%s/discussion.xml' % model.uid).lower()


def get_binaryfile_path(model):
    return ('I_{}/{}/{}'.format(model.uid, model.path.strip('/'), model.name)).lower()


def get_ressource_path(model):
    modelclassname = model.__class__.__name__
    targetfname = ('get_%s_path' % modelclassname).lower()
    targetfunc = globals().get(targetfname, None)
    if targetfunc:
        return targetfname(model)
    else:
        raise NotImplementedError()
