# -*- coding: utf-8 -*-
import ezdisteach.lib.odf
from ezdisteach.lib.naturalspecs.itemparser import get_item_from_instruction
from ezdisteach.lib.odf.tools import normalize_text, parse_note_slide_toml
from ezdisteach.model import create_model


def section_builder(odpdocument, section, **kwargs):
    # Treat the childen [0] for info
    currentslide = kwargs.get('slide', None)
    if currentslide is None:
        raise NotImplementedError()
    sectiontitle = ""
    sectiondoc = currentslide.children[0]
    pclass = sectiondoc.attributes.get('presentation:class', None)
    if pclass:
        sectiontitle = sectiondoc.text_content

    section.title = sectiontitle

    presentationnotes = currentslide.children[-1]

    tomlconfig, embedded = parse_note_slide_toml(presentationnotes.text_content)
    # We should have
    # draw:frame
    #   draw:text-box
    #       text:list
    #
    bulletindex = 0
    for frame in currentslide.children[1:-1]:
        # we look for the bullets /text:list
        bullets = frame.get_elements('draw:text-box/text:list/text:list-item')
        for bullet in bullets:
            # Here we recreate the item as it can be anything from label to assignment
            content = normalize_text(bullet.text_content)
            if content:
                type, args = get_item_from_instruction(content, "fr")
                if type:
                    item = create_model(type)
                    section.insert(bulletindex, item)
                    args['noteparams'] = (tomlconfig, embedded)
                    builder = ezdisteach.lib.odf.build_model(odpdocument, item, **args)
