""" Test content types
"""


import os
import pyramid
import unittest
import webtest
import xmltodict


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


class XmlRendererFactory:

    MEDIA_TYPE = 'application/xml'

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = ''
        request = system['request']
        response = request.response
        response.content_type = self.MEDIA_TYPE
        result = xmltodict.unparse(value)
        return result


class TestAccept(unittest.TestCase):

    def setUp(self):
        self.input_text = 'test text'
        self.output_text = self.input_text.capitalize()
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)
        self.config.add_renderer('xml', XmlRendererFactory)
        self.config.set_media_renderer('application/xml', 'xml')
        self.config.scan('.content_types')
        self.test_application = webtest.TestApp(self.config.make_wsgi_app())
        return None

    def tearDown(self):
        pyramid.testing.tearDown()
        return None

    def test_accept_json(self):
        response = self.accept_media_type('application/json')
        text = response.json['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_accept_text(self):
        response = self.accept_media_type('text/plain')
        return None

    def test_accept_xml(self):
        response = self.accept_media_type('application/xml')
        text = xmltodict.parse(response.body)['text']
        self.assertEqual(text, self.output_text)
        return None

    def accept_media_type(self, media_type):
        response = self.test_application.put_json(
            '/v0.0/capitalize',
            {'text': self.input_text},
            headers={
                'Accept': media_type,
            },
            status=200,
        )
        self.assertTrue(
            response.headers['Content-Type'].startswith(media_type),
        )
        return response


# EOF
