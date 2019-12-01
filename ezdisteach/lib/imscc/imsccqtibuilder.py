import xml.etree.ElementTree as ET
from io import StringIO

from ezdisteach.lib.tools import generate_uid
from ezdisteach.model.assessment.assessment import Assessment
from .tools import get_ressource_path

IMS_QTI_VERSION_1P2 = "1.2"
IMSCC_QTI_MANIFEST_INFO = {
    IMS_QTI_VERSION_1P2: {
        None: "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instancet",
    }
}


def _add_metadata_entries(metadatafieldset, parentelement, fieldsetelementname='qtimetadatafield'):
    for fe in metadatafieldset:
        qtimetadatafield = ET.SubElement(parentelement, fieldsetelementname)
        fieldlabel = ET.SubElement(qtimetadatafield, 'fieldlabel')
        fieldentry = ET.SubElement(qtimetadatafield, 'fieldentry')
        label, entry = fe
        fieldlabel.set_text(label)
        fieldentry.set_text(entry)


def _add_mat_text(parentelement, textcontent, texttype='text/html'):
    material = ET.SubElement(parentelement, 'material')
    materialtext = ET.SubElement(parentelement, 'mattext', {'texttype': texttype})
    materialtext.set_text('<![CDATA[%s]]' % textcontent)


def _add_flow_mat_text(parentelement, textcontent, texttype='text/html'):
    flowmat = ET.SubElement(parentelement, 'flow_mat')
    material = ET.SubElement(parentelement, 'flow_mat')
    _add_mat_text(material, textcontent, texttype)


def _add_respcondition(parentelement, response_lid_id, questionmodel, title,
                       iscontinue=False,
                       score=None,
                       feedbackid=None):
    respcondition = ET.SubElement(parentelement, 'respcondition',
                                  {'title': title, 'continue': 'Yes' if iscontinue else 'No'})
    conditionvar = _get_condition_var(None, response_lid_id, questionmodel)
    respcondition.append(conditionvar)

    if score:
        scoreelt = ET.SubElement(respcondition, 'setvar', {'varname': 'SCORE', 'action': 'set'})
        scoreelt.set_text(score)

    # Add display feedback
    if feedbackid:
        ET.SubElement(respcondition, 'displayfeedback', {'feedbacktype': 'Response', 'linkrefid': feedbackid})


GENERIC_RESPONSES = ['general', 'correct', 'incorrect']


def _add_respconditions(respprocessingel, response_lid_id, questionmodel, feedbacks):
    minscore = questionmodel.meta.get('minscore', 0)
    maxscore = questionmodel.meta.get('maxscore', 100)

    # Add generic response conditions
    for responsetype in GENERIC_RESPONSES:
        title = None
        iscontinue = False
        feedbackid = _get_fb_uid(responsetype, questionmodel)
        score = None
        if responsetype == 'general':
            iscontinue = True
        if responsetype == 'correct':
            score = maxscore
        if responsetype == 'incorrect':
            score = minscore
        _add_respcondition(respprocessingel, response_lid_id, questionmodel, title,
                           iscontinue=iscontinue,
                           score=score,
                           feedbackid=feedbackid)
    # Add other feedback
    for fbkey, fbvalue in feedbacks.items():
        if fbkey in ['general', 'correct', 'incorrect']:
            continue  # We already have added these ones
        title = None
        iscontinue = False
        feedbackid = _get_fb_uid(fbkey, questionmodel)
        score = None
        _add_respcondition(respprocessingel, response_lid_id, questionmodel, title,
                           iscontinue=iscontinue,
                           score=score,
                           feedbackid=feedbackid)


def _get_fb_uid(fbkey, questionmodel):
    uid = ''
    if fbkey in GENERIC_RESPONSES:
        uid = fbkey
    else:
        uid = questionmodel.get_choice_uid(fbkey).upper()
    return 'I%s_fb' % uid


def _get_condition_var(rigthanswers, response_lid_id, questionmodel):
    conditionvar = ET.Element('conditionvar')
    if rigthanswers is None:
        ET.SubElement(conditionvar, 'other')
    else:
        parentelement = conditionvar
        if len(rigthanswers) > 1:
            parentelement = ET.Element('or')
        for ra in rigthanswers:
            varequal = ET.SubElement(parentelement, 'varequal', {'respident': response_lid_id})
            varequal.set_text(('I_%s' % questionmodel.get_choice_uid(ra)).upper())
    return conditionvar


def multiplechoice_xmlqti_builder(questionmodel, rootdocument: ET.ElementTree = None,
                                  itemparent: ET.Element = None,
                                  imsqtiversion=IMS_QTI_VERSION_1P2):
    # General metadata
    itemmetadata = ET.SubElement(itemparent, 'itemmetadata')
    qtimetadata = ET.SubElement(itemmetadata, 'qtimetadata')
    FIELD_ENTRY = [('cc_profile', 'cc.multiple_choice.v0p1'),
                   ('cc_question_category', questionmodel.meta.get('category', '')),
                   ]

    _add_metadata_entries(FIELD_ENTRY, qtimetadata)

    # Presentation aspects
    presentation = ET.SubElement(itemparent, 'presentation')
    _add_mat_text(presentation, questionmodel.intro)

    # Response LID
    responselid = ET.SubElement(presentation, 'response_lid')
    # Response LID Identifier has only one visible use: in the respcondition
    responselid_identifier = generate_uid()
    responselid.set('ident', ('I_%s' % responselid_identifier).upper())
    renderchoice = ET.SubElement(responselid, 'render_choice')
    shufflevalue = 'Yes' if questionmodel.meta.get('shuffle', False) else 'No'
    renderchoice.set('shuffle', shufflevalue)
    for chkey, chvalue in questionmodel.meta.get('feedbacks', {}).items():
        responselabel = ET.SubElement(renderchoice, 'response_label')
        responselabel.set('ident', ('I_%s' % questionmodel.get_choice_uid(chkey)).upper())
        _add_mat_text(responselabel, chvalue)

    # Response processing
    resprocessing = ET.SubElement(itemparent, 'resprocessing')
    outcomes = ET.SubElement(resprocessing, 'outcomes')

    minscore = questionmodel.meta.get('minscore', 0)
    maxscore = questionmodel.meta.get('maxscore', 100)

    ET.SubElement(outcomes, 'decvar',
                  {'varname': 'SCORE', 'vartype': 'Decimal',
                   'minvalue': minscore,
                   'maxvalue': maxscore})

    generalfb = questionmodel.meta.get('generalfeedback', None)
    feedbacks = questionmodel.meta.get('feedbacks', {})
    _add_respconditions(resprocessing, responselid_identifier, questionmodel, feedbacks)
    # Feedback
    allfb = {fbkey: fbkey.capitalize() for fbkey in GENERIC_RESPONSES}
    allfb.update(feedbacks)  # Make sure we got default values
    for fbkey, fbvalue in feedbacks.items():
        itemfeedback = ET.SubElement(itemparent, 'itemfeedback')
        itemfeedback.set('ident', _get_fb_uid(fbkey, questionmodel))
        _add_flow_mat_text(itemfeedback, fbvalue)


def course_xmlqti_builder(coursemodel, imsqtiversion=IMS_QTI_VERSION_1P2):
    qtis_xml = {}
    for section in coursemodel:
        for item in section:
            if isinstance(item, Assessment):
                # Get the model path
                path = get_ressource_path(item)
                stream = StringIO(get_xml_qti_for_asssement(item, imsqtiversion))
                qtis_xml.set(path, stream)
    return qtis_xml


# See https://www.imsglobal.org/question/qtiv1p2/imsqti_asi_infov1p2.html (4.1)

def get_xml_qti_for_asssement(assessmentmodel: Assessment,
                              imsqtiversion=IMS_QTI_VERSION_1P2):
    imsmetaattributes = IMSCC_QTI_MANIFEST_INFO.get(imsqtiversion, None)

    questestinterop = ET.Element('questestinterop')
    rootdocument = ET.ElementTree(questestinterop)

    for mkey, mvalue in imsmetaattributes.items():
        questestinterop.set('xmlns:%s' % mkey if mkey else 'xmlns', mvalue)
    questestinterop.set("xsi:schemaLocation", " ".join([val for val in imsmetaattributes.values()]))
    assessment = ET.SubElement(questestinterop, 'assessment')
    assessment.set('ident', ('QBD_%s' % assessmentmodel.uid).upper())
    assessment.set('title', 'QBD_%s' % assessmentmodel.model.test)

    qtimetadata = ET.SubElement(assessment, 'qtimetadata')

    # TODO see if that can be taken from the model
    FIELD_ENTRY = [('cc_profile', 'cc.exam.v0p1'),
                   ('qmd_assessmenttype', 'Examination'),
                   ('qmd_scoretype', 'Percentage'),
                   ('qmd_feedbackpermitted', 'Yes'),
                   ('qmd_hintspermitted', 'Yes'),
                   ('qmd_solutionspermitted', 'Yes'),
                   ]

    _add_metadata_entries(FIELD_ENTRY, qtimetadata)

    rubric = ET.SubElement(assessment, 'rubric')
    material = ET.SubElement(rubric, 'material')
    material.set('label', 'Summary')  # TODO there should be some language dependent string here
    mattext = ET.SubElement(material, 'mattext')
    mattext.set_text('<![CDATA[%s]]' % assessmentmodel.title)

    section = ET.SubElement(assessment, 'section')
    assessment.set('ident', ('I_%s' % assessmentmodel.uid).upper())
    # Now we add each assesment items (questions)
    for qmodel in assessmentmodel:
        build_xml_qti_for_question(qmodel, rootdocument, section, imsqtiversion)


def build_xml_qti_for_question(questionmodel, rootdocument: ET.ElementTree = None,
                               itemparent: ET.Element = None,
                               imsqtiversion=IMS_QTI_VERSION_1P2):
    modelclassname = questionmodel.__class__.__name__
    builderfunctname = '%s_xmlqti_builder' % modelclassname.lower()
    builderfunct = globals().get(builderfunctname, None)
    if builderfunct:
        return builderfunct(questionmodel, rootdocument, itemparent, imsqtiversion)
    else:
        raise NotImplementedError(
            'cannot find xml qti builder function {} for {}'.format(builderfunctname, modelclassname))
