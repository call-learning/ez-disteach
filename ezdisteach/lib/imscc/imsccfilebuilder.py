# -*- coding: utf-8 -*-
"""
    IMSCC File Builder
    Produce an lxml entity ready to convert to text
"""

import io


def course_output_file(model, ioopen=io.open) -> None:
    for item in model:
        file_output(item, ioopen)


def section_output_file(model, ioopen=io.open) -> None:
    for item in model:
        file_output(item, ioopen)


def label_output_file(model, ioopen=io.open) -> None:
    pass


def assessment_output_file(model, ioopen=io.open) -> None:
    pass


def discussion_output_file(model, ioopen=io.open) -> None:
    # Output the discussion.xml file
    pass


def binaryfile_output_file(model, ioopen=io.open) -> None:
    with ioopen(model.name, 'w') as f:
        f.write(model.export())


def image_output_file(model, ioopen=io.open) -> None:
    with ioopen(model.name, 'w') as f:
        f.write(model.export())


def file_output(model, ioopen=io.open):
    modelclassname = model.__class__.__name__
    builderfunctname = '%s_output_file' % modelclassname.lower()
    builderfunct = globals().get(builderfunctname, None)
    if builderfunct:
        return builderfunct(model, ioopen)
    else:
        raise NotImplementedError(
            'cannot find file output builder function {} for {}'.format(builderfunctname, modelclassname))
