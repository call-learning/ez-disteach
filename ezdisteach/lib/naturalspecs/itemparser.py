# -*- coding: utf-8 -*-

import re
import unicodedata

import spacy

from .tools import get_model_class_list

SPACY_LOAD_LANG = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}


def _filter_shortest_spans(spans):
    """Filter a sequence of spans and remove duplicates or overlaps. Useful for
    creating named entities (where one token can only be part of one entity) or
    when merging spans with `Retokenizer.merge`.
    At the oposite of the spacy.util.filter_spans
    when spans overlap, the (first) shortest span is preferred over longer spans.

    spans (iterable): The spans to filter.
    RETURNS (list): The filtered spans.
    """
    get_sort_key = lambda span: (span.end - span.start, span.start)
    sorted_spans = sorted(spans, key=get_sort_key)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result


QUOTED_TEXT_REGEXP = r'\"(.+?)\"'
ARG_ROOT_NAME = "ARG_"


def get_quoted_text(instructions):
    """
    Get a list of quoted terms
    :param instructions:
    :return:
    """
    return [quoted for quoted in re.findall(QUOTED_TEXT_REGEXP, instructions)]


def replace_quoted_text(instructions):
    """
    Replaces any quoted string with ARG_1, ARG_2 and so on
    :param instructions:
    :return:
    """

    index = 0
    result = ""
    lastmatchpos = 0
    for matchobj in re.finditer(QUOTED_TEXT_REGEXP, instructions):
        result += instructions[lastmatchpos:matchobj.start()]
        result += ARG_ROOT_NAME + str(index)
        lastmatchpos = matchobj.end()
        index += 1
    result += instructions[lastmatchpos::]
    return result


def get_tokens_from_instruction(instructions, lang="fr"):
    """
    Get instructions from a very simplified natural language type of instruction such as:
    Un lien vers "http://www.wikipedia.org"
    Un lien nommé "Wikipedia" vers "http://www.wikipedia.org"

    They are transformed into a Tree


    :param instructions:
    :param lang:
    :return: A tree
    """

    nlp = spacy.load(SPACY_LOAD_LANG.get(lang, 'fr'))
    doc = nlp(replace_quoted_text(instructions))
    return [(w.pos_, w.text, w.ent_type_) for w in doc if not w.is_stop and not w.is_punct]


def _get_model_from_type(type):
    availablemodels = dict((modelname.lower(), modelname) for modelname in get_model_class_list())
    normalizedtype = unicodedata.normalize('NFD', type.lower()).encode('ascii', 'ignore').decode('utf-8')
    if normalizedtype in availablemodels.keys():
        return availablemodels.get(normalizedtype)
    return None


def get_item_from_instruction(instruction, lang="fr"):
    tokens = get_tokens_from_instruction(instruction, lang)
    newtype =""
    if tokens:
        type = tokens[0][1]
        buildargs = dict(
            (ARG_ROOT_NAME + str(index), match) for index, match in enumerate(get_quoted_text(instruction)))
        args = [t[1] for t in tokens if t[2] != '']

        # TODO make sure we translate back to english
        if type == 'lien':
            newtype = 'Link'
        elif type == 'quiz':
            newtype = 'Assessment'
        else:
            newtype = _get_model_from_type(type)

        if newtype is None:
            UnsupportedItem('Cannot find the Model correponding to %s' % type)

        # TODO: this part has to be rethought completely. We should have a TextCategorizer or EntityRuler doing this
        # As we have equivalent words (tile => nommé, named, nommée)...
        argsvalue = {}
        argsvalue['title'] = buildargs[ARG_ROOT_NAME + '0']
        # TODO: rework this
        if newtype == 'Video' or newtype == 'Link':
            argsvalue['url'] = buildargs[ARG_ROOT_NAME + '1']
        return [newtype, argsvalue]
    raise UnsupportedItem('Cannot parse the instruction:%s' % instruction)

class UnsupportedItem(Exception):
    """Cannot decode the instruction"""
