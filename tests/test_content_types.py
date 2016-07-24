""" Test content types
"""


import json
import os

import apiramid
import pyramid.testing
import unittest
import webtest
import xmltodict


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


@apiramid.endpoint.EndpointDefaults(path='/capitalize', deserialize=True)
class Capitalize(object):

    def __init__(self, context, request):
        self.request = request
        return None

    def capitalize(self):
        text = self.request.dict_body.get('text', '')
        result = {
            'text': text.capitalize(),
        }
        return result

    @apiramid.endpoint.Endpoint(request_method='PUT')
    def put(self):
        result = self.capitalize()
        return pyramid.httpexceptions.HTTPOk(
            body=result,
        )


class XmlRendererFactory:

    MEDIA_TYPE = 'application/xml'

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system['request']
        response = request.response
        response.content_type = self.MEDIA_TYPE
        result = xmltodict.unparse(value)
        return result


class XmlDeserializerFactory:

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = xmltodict.parse(value)
        return result


class JsonDeserializerFactory:

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = system['request'].json_body
        return result


class TestAccept(unittest.TestCase):

    def setUp(self):
        self.path = '/v0.0/capitalize'
        self.expected_status = 200
        self.input_text = "test text"
        self.input_dict = {'text': self.input_text}
        self.output_text = self.input_text.capitalize()
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)

        self.config.add_renderer('xml', XmlRendererFactory)
        self.config.set_media_renderer('application/xml', 'xml')

        self.config.add_deserializer('xml', XmlDeserializerFactory)
        self.config.set_media_deserializer('application/xml', 'xml')

        self.config.add_deserializer('json', JsonDeserializerFactory)
        self.config.set_media_deserializer('application/json', 'json')

        self.config.scan('.')
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
