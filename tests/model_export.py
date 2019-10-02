import re
import unittest

from ezdisteach.model import create_model


class TestModelExport(unittest.TestCase):
    _basic_course = None

    def setUp(self):
        self._basic_course = create_model('Course',
                                          languages=['en'],
                                          title='Course Title',
                                          description='Course Description <span> Span</span>',
                                          keywords=['tag1', 'tag2'])

    def tearDown(self):
        self._basic_course = None

    def test_course_imscc_export(self):
        self._basic_course.append(create_model('Section', title='Section 1'))
        self._basic_course[0].append(create_model('Label', title='Label Title', description='Label Descripton'))
        stream = self._basic_course.imscc_meta
        # We know that it is a stringio that is returned but it should not be assumed
        currentvalue = stream.getvalue()
        replaceident = re.compile(r'identifier="(\w+)"')
        currentvalue  = replaceident.sub('identifier="AAAAAAA"', currentvalue)
        self.assertEqual(currentvalue, BASIC_IMS_CONTENT)


BASIC_IMS_CONTENT = '''<?xml version='1.0' encoding='utf-8'?>
<manifest identifier="AAAAAAA" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.w3.org/2001/XMLSchema-instance">
  <metadata>
    <schema>
      IMS Common Cartridge
    </schema>
    <schemaversion>
      1.1.0
    </schemaversion>
    <lomimscc:lom>
      <lomimscc:general>
        <lomimscc:title>
          <lomimscc:string>
            Course Title
          </lomimscc:string>
        </lomimscc:title>
        <lomimscc:description>
          <lomimscc:string>
            Course Description &lt;span&gt; Span&lt;/span&gt;
          </lomimscc:string>
        </lomimscc:description>
        <lomimscc:keyword>
          <lomimscc:string>
            tag1
          </lomimscc:string>
        </lomimscc:keyword>
        <lomimscc:keyword>
          <lomimscc:string>
            tag2
          </lomimscc:string>
        </lomimscc:keyword>
      </lomimscc:general>
    </lomimscc:lom>
  </metadata>
  <organization identifier="AAAAAAA" structure="rooted-hierarchy">
    <item identifier="AAAAAAA" />
    <item>
      <title>
        Section 1
      </title>
      <item>
        <title>
          Label Title
        </title>
      </item>
    </item>
  </organization>
  <resources />
</manifest>'''
