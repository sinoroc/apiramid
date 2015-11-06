""" Test content types
"""


import dicttoxml
import os
import pyramid
import unittest
import webtest


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


class XmlRendererFactory:

    CONTENT_TYPE = 'application/xml'

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = ''
        request = system['request']
        response = request.response
        response.content_type = self.CONTENT_TYPE
        result = dicttoxml.dicttoxml(value)
        return result


class TestAccept(unittest.TestCase):

    def setUp(self):
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)
        self.config.add_renderer('xml', XmlRendererFactory)
        self.config.set_mime_renderer('application/xml', 'xml')
        self.config.scan('.content_types')
        self.test_application = webtest.TestApp(self.config.make_wsgi_app())
        return None

    def tearDown(self):
        pyramid.testing.tearDown()
        return None

    def test_accept_json(self):
        response = self.accept_mime_type('application/json')
        self.assertEqual(response.json['text'], 'Test text')
        return None

    def test_accept_text(self):
        response = self.accept_mime_type('text/plain')
        return None

    def test_accept_xml(self):
        response = self.accept_mime_type('application/xml')
        return None

    def accept_mime_type(self, mime_type):
        response = self.test_application.put_json(
            '/v0.0/capitalize',
            {'text': 'test text'},
            headers={
                'Accept': mime_type,
            },
            status=200,
        )
        self.assertTrue(
            response.headers['Content-Type'].startswith(mime_type),
        )
        return response


# EOF
