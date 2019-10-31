# -*- coding: utf-8 -*-
import toml
import ezdisteach.lib.odf

from odfdo import Frame, DrawPage, Element
from ezdisteach.lib.odf.tools import normalize_note_section
from ezdisteach.model import create_model, ImportationError


def course_builder(odpdocument, coursemodel, **kwargs):
    firstslide = odpdocument.body.children[0]
    if not firstslide:
        raise ImportationError('odpcourse', 'Course', 'no first slide')
    coursetitle, coursedesc, langs, tags = _get_course_information(firstslide)

    coursemodel.title = coursetitle
    coursemodel.description = coursedesc
    coursemodel.languages = langs
    coursemodel.keywords = tags

    slideindex = 0
    for slide in odpdocument.body.children[1:]:
        if slide.__class__ is DrawPage:
            try:
                section = coursemodel[slideindex]
            except IndexError:
                section = create_model('Section')
                coursemodel.insert(slideindex, section)
            ezdisteach.lib.odf.build_model(odpdocument, section, slide=slide)
            slideindex += 1


def _get_course_information(slide):
    """
    Return basic course information from the main slide such as title, description, langs, tags
    :param maindocument:
    :return: list of information coursetitle, coursedesc, langs, tags
    """

    titletag = next((e for e in slide.children if e.get_attribute('presentation:class') == 'title'),
                    None)
    shortdescriptiontag = next((e for e in slide.children if
                                e.get_attribute('presentation:class') == 'subtitle'), None)
    otherdescriptions = (e for e in slide.children if
                         isinstance(e, Frame) and not (
                                 e.get_attribute('presentation:class') in ('title', 'subtitle')))
    coursetitle = titletag.text_content if titletag else ""
    coursedesc = shortdescriptiontag.text_content if shortdescriptiontag else ""
    coursedesc += ','.join((t.get_formatted_text({}) for t in otherdescriptions))

    langs = []
    tags = []
    try:
        # Now decode the notes to add tags and language if it exists
        notetag = next(
            (e for e in slide.children if isinstance(e, Element) and e.tag == 'presentation:notes'), None)
        configcontent = normalize_note_section(notetag.text_content)
        parsednotes = toml.loads(configcontent)
        meta = parsednotes.get('meta', None)
        if meta is not None:
            tags = meta.get('tags', [])
            langs = [l.strip() for l in meta.get('langs', [])]
    except Exception as e:
        raise ImportationError('odpcourse', 'Course', 'Cannot parse presentation Notes:' + str(e))
    return (coursetitle, coursedesc, langs, tags)
