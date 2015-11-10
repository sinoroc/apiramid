""" Test content types
"""


import json
import os
import pyramid.testing
import unittest
import webtest
import xmltodict

from . import content_types


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


class TestAccept(unittest.TestCase):

    def setUp(self):
        self.path = '/v0.0/capitalize'
        self.expected_status = 200
        self.input_text = 'test text'
        self.input_dict = {'text': self.input_text}
        self.output_text = self.input_text.capitalize()
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)

        self.config.add_renderer('xml', content_types.XmlRendererFactory)
        self.config.set_media_renderer('application/xml', 'xml')

        self.config.add_deserializer('xml', content_types.XmlDeserializerFactory)
        self.config.set_media_deserializer('application/xml', 'xml')

        self.config.add_deserializer('json', content_types.JsonDeserializerFactory)
        self.config.set_media_deserializer('application/json', 'json')

        self.config.scan('.content_types')
        self.test_application = webtest.TestApp(self.config.make_wsgi_app())
        return None

    def tearDown(self):
        pyramid.testing.tearDown()
        return None

    def test_json_to_json(self):
        response = self.json_to_media_type('application/json')
        text = response.json['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_json_to_text(self):
        response = self.json_to_media_type('text/plain')
        return None

    def test_json_to_xml(self):
        response = self.json_to_media_type('application/xml')
        text = xmltodict.parse(response.body)['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_xml_to_json(self):
        response = self.xml_to_media_type('application/json')
        text = response.json['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_xml_to_text(self):
        response = self.xml_to_media_type('text/plain')
        return None

    def test_xml_to_xml(self):
        response = self.xml_to_media_type('application/xml')
        text = xmltodict.parse(response.body)['text']
        self.assertEqual(text, self.output_text)
        return None

    def json_to_media_type(self, media_type):
        body = json.dumps(self.input_dict)
        return self.request(body, 'application/json', media_type)

    def xml_to_media_type(self, media_type):
        body = xmltodict.unparse(self.input_dict)
        return self.request(body, 'application/xml', media_type)

    def request(self, body, content_type, accept):
        response = self.test_application.put(
            self.path,
            body,
            headers={
                'Content-Type': content_type,
                'Accept': accept,
            },
            status=self.expected_status,
        )
        self.assertTrue(
            response.headers['Content-Type'].startswith(accept),
        )
        return response


# EOF
