# -*- coding: utf-8 -*-
import re
from abc import abstractmethod, ABC

import toml
from odfdo import Document, Frame, DrawPage, Element

from ezdisteach.lib.naturalspecs.itemparser import get_item_from_instruction
from ezdisteach.model import create_model, ImportationError
import aiken
from ezdisteach.lib.quiztext.aiken import parse_aiken_quiz

class BaseModelBuilder(ABC):
    def __init__(self, fulldocument: Document, currentmodel):
        self.odpdocument = fulldocument
        self.currentmodel = currentmodel

    @abstractmethod
    def build(self, docitem=None, **kwargs):
        pass


class CourseModelBuilder(BaseModelBuilder):

    def build(self, docitem=None, **kwargs):
        firstslide = self.odpdocument.body.children[0]
        if not firstslide:
            raise ImportationError('odpcourse', 'Course', 'no first slide')
        coursetitle, coursedesc, langs, tags = self._get_course_information(firstslide)

        course = self.currentmodel
        course.title = coursetitle
        course.description = coursedesc
        course.languages = langs
        course.keywords = tags

        slideindex = 0
        for slide in self.odpdocument.body.children[1:]:
            if slide.__class__ is DrawPage:
                try:
                    section = course[slideindex]
                except IndexError:
                    section = create_model('Section')
                    course.insert(slideindex, section)
                builder = build_model(self.odpdocument, section)
                builder.build(slide)
                slideindex += 1

    @staticmethod
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


class SectionModelBuilder(BaseModelBuilder):

    def build(self, docitem=None, **kwargs):
        # Treat the childen [0] for info
        if docitem is None:
            raise NotImplementedError()
        sectiontitle = ""
        sectiondoc = docitem.children[0]
        pclass = sectiondoc.attributes.get('presentation:class', None)
        if pclass:
            sectiontitle = sectiondoc.text_content

        section = self.currentmodel
        section.title = sectiontitle

        presentationnotes = docitem.children[-1]

        tomlconfig, embedded = parse_note_slide_toml(presentationnotes.text_content)
        # We should have
        # draw:frame
        #   draw:text-box
        #       text:list
        #
        bulletindex = 0
        for frame in docitem.children[1:-1]:
            # we look for the bullets /text:list
            bullets = frame.get_elements('draw:text-box/text:list/text:list-item')
            for bullet in bullets:
                # Here we recreate the item as it can be anything from label to assignment
                content = normalize_text(bullet.text_content)
                if content:
                    iteminstr, args = get_item_from_instruction(content, "fr")
                    if iteminstr:
                        type = iteminstr
                        item = create_model(type)
                        section.insert(bulletindex, item)
                        builder = build_model(self.odpdocument, item)
                        args['noteparams'] = (tomlconfig, embedded)
                        item = builder.build(bullet, **args)


class VideoModelBuilder(BaseModelBuilder):
    def build(self, docitem=None, **kwargs):
        if docitem is None:
            raise NotImplementedError()
        self.currentmodel.title = kwargs.get('title')
        self.currentmodel.url = kwargs.get('url', None)


class LinkModelBuilder(BaseModelBuilder):
    def build(self, docitem=None, **kwargs):
        if docitem is None:
            raise NotImplementedError()
        self.currentmodel.title = kwargs.get('title')
        self.currentmodel.url = kwargs.get('url', None)


class LabelModelBuilder(BaseModelBuilder):
    def build(self, docitem=None, **kwargs):
        if docitem is None:
            raise NotImplementedError()
        self.currentmodel.title = kwargs.get('title')


class ImageModelBuilder(BaseModelBuilder):
    def build(self, docitem=None, **kwargs):
        if docitem is None:
            raise NotImplementedError()
        self.currentmodel.title = kwargs.get('title')
        self.currentmodel.url = kwargs.get('url', None)


class AssessmentModelBuilder(BaseModelBuilder):
    def build(self, docitem=None, **kwargs):
        if docitem is None:
            raise NotImplementedError()
        self.currentmodel.title = kwargs.get('title')
        # Now try to find  the config for this quiz in the note
        quizcontent = ""
        quizformat = ""
        tomlconfig, embedded = kwargs.get('noteparams')
        if tomlconfig.get('quiz'):
            quizindex = 0
            for quizdef in tomlconfig.get('quiz'):
                if tomlconfig['quiz'][quizdef].get('name', None) == kwargs.get('title'):
                    quizformat = tomlconfig['quiz'][quizdef].get('type')
                    quizcontent = embedded[quizindex]
        if quizcontent and quizformat:
            # TODO manage more formats
            if quizformat == "aiken":
                # This library will have to be implemented !!!
                # questions = aiken.load(quizcontent)
                result = parse_aiken_quiz(SIMPLE_AIKEN)
                qs = ['Is it this one?', 'Maybe this answer?','Possibily this one ?', 'Must be this one!']
                chx = [3] # 4th choice
                item = create_model('MultipleChoice', title='Title of the question',questions=qs, rightchoices=chx )



def build_model(fulldocument: Document, currentmodel):
    modelclassname = currentmodel.__class__.__name__
    builderclassname = '%sModelBuilder' % modelclassname
    builderclass = globals().get(builderclassname, None)
    if builderclass:
        return builderclass(fulldocument, currentmodel)
    else:
        raise NotImplementedError('cannot find %sModelBuilder' % modelclassname)


def normalize_text(content):
    # Replace other characters
    content = re.sub(r'(«\s*|\s*»)', lambda match: "\"", content, flags=re.UNICODE)

    charmap = {0x201c: u'"',  # Opening quote
               0x201d: u'"',  # Closing quote
               0x00A0: u' ',  # Non breaking space
               0x2018: u'"',
               0x2019: u'"'
               }  # We remove smart quotes
    content = content.translate(charmap)
    return content


def normalize_note_section(content):
    # first make sure that tags are in lower case
    content = re.sub(r'^\[(.*)\]', lambda match: match.group(0).lower(), content, flags=re.MULTILINE)

    # secondly make sure that assigned variables names are also lowercase
    content = re.sub(r'^(.*)\s*\=', lambda match: match.group(0).lower(), content, flags=re.MULTILINE)

    content = normalize_text(content)
    # We remove comments
    content = re.sub(r'^#.*\n?', '', content, flags=re.MULTILINE)
    return content


TOML_MODE = 1
EMBEDDED_CONTENT = 2


def parse_note_slide_toml(noteslidecontent):
    configcontent = normalize_text(noteslidecontent)
    # Make sure all the opening bracked start on the first column
    configcontent = re.sub(r'^\s*\[', '[', configcontent)

    # Split embedded content and TOML

    mode = TOML_MODE
    tomlstring = ""
    embedded = []
    currentembedded = ""
    for line in configcontent.splitlines():
        if line.startswith('---'):
            if mode == TOML_MODE:
                mode = EMBEDDED_CONTENT
                currentembedded = ""
            else:
                mode = TOML_MODE
                embedded.append(currentembedded)
        else:
            if mode == TOML_MODE:
                tomlstring += '\n%s' % line
            else:
                currentembedded += '\n%s' % line

    tomlstring = normalize_note_section(tomlstring)
    tomlconfig = toml.loads(tomlstring)

    return tomlconfig, embedded
