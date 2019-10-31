# -*- coding: utf-8 -*-

import re
import toml

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
