""" Test content types
"""


# pylint: disable=duplicate-code


import json
import os
import unittest

import apiramid
import pyramid.testing
import webtest
import xmltodict


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


@apiramid.endpoint.EndpointDefaults(path='/capitalize', deserialize=True)
class Capitalize:
    """ Capitalize endpoint
    """

    def __init__(self, context, request):
        dummy = context
        self.request = request
        return None

    def capitalize(self):
        """ Capitalize the 'text' field of the request's JSON body.
        """
        text = self.request.dict_body.get('text', '')
        result = {
            'text': text.capitalize(),
        }
        return result

    @apiramid.endpoint.Endpoint(request_method='PUT')
    def put(self):
        """ View callable for PUT method.
        """
        result = self.capitalize()
        return pyramid.httpexceptions.HTTPOk(
            body=result,
        )


class XmlRendererFactory:  # pylint: disable=too-few-public-methods
    """ Renderer factory for XML media type
    """

    MEDIA_TYPE = 'application/xml'

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system['request']
        response = request.response
        response.content_type = self.MEDIA_TYPE
        result = xmltodict.unparse(value)
        return result


class XmlDeserializerFactory:  # pylint: disable=too-few-public-methods
    """ Deserializer factory for XML media type
    """

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = xmltodict.parse(value)
        return result


class JsonDeserializerFactory:  # pylint: disable=too-few-public-methods
    """ Deserializer factory for JSON media type
    """

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = system['request'].json_body
        return result


class TestAccept(unittest.TestCase):
    """ Test cases for content types in HTTP header 'Accept'
    """

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
        """ Test case for JSON to JSON
        """
        response = self.json_to_media_type('application/json')
        text = response.json['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_json_to_text(self):
        """ Test case for JSON to text
        """
        self.json_to_media_type('text/plain')
        return None

    def test_json_to_xml(self):
        """ Test case for JSON to XML
        """
        response = self.json_to_media_type('application/xml')
        text = xmltodict.parse(response.body)['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_xml_to_json(self):
        """ Test case for XML to JSON
        """
        response = self.xml_to_media_type('application/json')
        text = response.json['text']
        self.assertEqual(text, self.output_text)
        return None

    def test_xml_to_text(self):
        """ Test case for XML to text
        """
        self.xml_to_media_type('text/plain')
        return None

    def test_xml_to_xml(self):
        """ Test case for XML to XML
        """
        response = self.xml_to_media_type('application/xml')
        text = xmltodict.parse(response.body)['text']
        self.assertEqual(text, self.output_text)
        return None

    def json_to_media_type(self, media_type):
        """ Helper to test a request with JSON body
        """
        body = json.dumps(self.input_dict)
        return self.request(body, 'application/json', media_type)

    def xml_to_media_type(self, media_type):
        """ Helper to test a request with XML body
        """
        body = xmltodict.unparse(self.input_dict)
        return self.request(body, 'application/xml', media_type)

    def request(self, body, content_type, accept):
        """ Helper to test a request
        """
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
