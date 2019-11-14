import re
import unittest

from ezdisteach.model import create_model


class TestModelIMSCCExport(unittest.TestCase):
    _basic_course = None

    def setUp(self):
        self._basic_course = create_model('Course',
                                          languages=['en'],
                                          title='Course Title',
                                          description='Course Description <span> Span</span>',
                                          keywords=['tag1', 'tag2'])
        question1 = create_model('MultipleChoice',
                                 title='Multiple choice 1',
                                 description='Multiple choice description',
                                 intro='Select what is the best LMS?',
                                 choices=dict([('A', 'Moodle'), ('B', 'edX'), ('C', 'Other')]),
                                 rightanswers=['A', 'B']
                                 )
        assessment = create_model('Assessment',
                                  title='Assessment',
                                  items=[question1])
        section = create_model('Section', items=[assessment])
        self._basic_course.append(section)


    def tearDown(self):
        self._basic_course = None

    def test_course_qti_export(self):
        self._basic_course.append(create_model('Section', title='Section 1'))
        self._basic_course[0].append(create_model('Label', title='Label Title', description='Label Descripton'))
        stream = self._basic_course.imscc_meta(metatype='qti')
        # We know that it is a stringio that is returned but it should not be assumed
        currentvalue = stream.getvalue()
        replaceident = re.compile(r'identifier="(\w+)"')
        currentvalue  = replaceident.sub('identifier="AAAAAAA"', currentvalue)
        self.assertEqual(currentvalue, BASIC_IMS_CONTENT)


BASIC_IMS_CONTENT = '''<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_qtiasiv1p2p1_v1p0.xsd">
    <assessment ident="QDB_A5EEB1D5" title="Test quiz">
        <qtimetadata>
            <qtimetadatafield>
                <fieldlabel>cc_profile</fieldlabel>
                <fieldentry>cc.exam.v0p1</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
                <fieldlabel>qmd_assessmenttype</fieldlabel>
                <fieldentry>Examination</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
                <fieldlabel>qmd_scoretype</fieldlabel>
                <fieldentry>Percentage</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
                <fieldlabel>qmd_feedbackpermitted</fieldlabel>
                <fieldentry>Yes</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
                <fieldlabel>qmd_hintspermitted</fieldlabel>
                <fieldentry>Yes</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
                <fieldlabel>qmd_solutionspermitted</fieldlabel>
                <fieldentry>Yes</fieldentry>
            </qtimetadatafield>
        </qtimetadata>
        <rubric>
            <material label="Summary">
                <mattext texttype="text/html">
                    <![CDATA[ Test quiz ]]>
                </mattext>
            </material>
        </rubric>
        <section ident="I_64591119">
            <item ident="I_7E66FD53" title="Test QCM">
                <itemmetadata>
                    <qtimetadata>
                        <qtimetadatafield>
                            <fieldlabel>cc_profile</fieldlabel>
                            <fieldentry>cc.multiple_choice.v0p1</fieldentry>
                        </qtimetadatafield>
                        <qtimetadatafield>
                            <fieldlabel>cc_question_category</fieldlabel>
                            <fieldentry>Quiz Bank 'Test quiz'</fieldentry>
                        </qtimetadatafield>
                    </qtimetadata>
                </itemmetadata>
                <presentation>
                    <material>
                        <mattext texttype="text/html">
                            <![CDATA[Select what is the best LMS?]]>
                        </mattext>
                    </material>
                    <response_lid rcardinality="Single" ident="AAAAAAA">
                        <render_choice shuffle="No">
                            <response_label ident="AAAAAAA">
                                <material>
                                    <mattext texttype="text/html">
                                        <![CDATA[ <p>Moodle</p> ]]>
                                    </mattext>
                                </material>
                            </response_label>
                            <response_label ident="AAAAAAA">
                                <material>
                                    <mattext texttype="text/html">
                                        <![CDATA[ <p>edX</p> ]]>
                                    </mattext>
                                </material>
                            </response_label>
                            <response_label ident="AAAAAAA">
                                <material>
                                    <mattext texttype="text/html">
                                        <![CDATA[ <p>Other</p> ]]>
                                    </mattext>
                                </material>
                            </response_label>
                        </render_choice>
                    </response_lid>
                </presentation>
                <resprocessing>
                    <outcomes>
                        <decvar varname="SCORE" vartype="Decimal" minvalue="0" maxvalue="100"/>
                    </outcomes>
                    <respcondition title="General feedback" continue="Yes">
                        <conditionvar>
                            <other/>
                        </conditionvar>
                        <displayfeedback feedbacktype="Response" linkrefid="general_fb"/>
                    </respcondition>
                    <respcondition title="Correct" continue="No">
                        <conditionvar>
                            <varequal respident="AAAAAAA">correct_fb</varequal>
                        </conditionvar>
                        <setvar varname="SCORE" action="Set">100</setvar>
                        <displayfeedback feedbacktype="Response" linkrefid="I_DF85ACEC_fb"/>
                    </respcondition>
                </resprocessing>
                <itemfeedback ident="AAAAAAA">
                    <flow_mat>
                        <material>
                            <mattext texttype="text/html">
                                <![CDATA[ <p>GeneralFeedback</p> ]]>
                            </mattext>
                        </material>
                    </flow_mat>
                </itemfeedback>

                <itemfeedback ident="AAAAAAA">
                    <flow_mat>
                        <material>
                            <mattext texttype="text/html">
                                <![CDATA[ Correct. ]]>
                            </mattext>
                        </material>
                    </flow_mat>
                </itemfeedback>
                <itemfeedback ident="AAAAAAA">
                    <flow_mat>
                        <material>
                            <mattext texttype="text/html">
                                <![CDATA[ <p>Incorrect</p> ]]>
                            </mattext>
                        </material>
                    </flow_mat>
                </itemfeedback>
            </item>
        </section>
    </assessment>
</questestinterop>
'''
