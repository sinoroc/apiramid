""" Test resources
"""


# pylint: disable=duplicate-code


import logging
import os
import unittest

import apiramid
import pyramid
import webtest


LOG = logging.getLogger(__name__)

PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


@apiramid.endpoint.EndpointDefaults(path='/bar/{id}')
class Bar:
    """ Endpoint 'bar'
    """

    def __init__(self, context, request):
        dummy = context
        self.request = request
        self.bar_id = int(request.matchdict['id'])
        return None

    @apiramid.endpoint.Endpoint(request_method='GET')
    def get(self):
        """ Method 'GET'
        """
        result = None
        body = {
            'name': 'bar',
            'id': self.bar_id,
        }
        result = pyramid.httpexceptions.HTTPOk(
            body=body,
        )
        return result

    @apiramid.endpoint.Endpoint(request_method='POST')
    def post(self):  # pylint: disable=no-self-use
        """ Method 'POST'
        """
        raise pyramid.httpexceptions.HTTPNotImplemented()

    @apiramid.endpoint.Endpoint(request_method='PUT')
    def put(self):  # pylint: disable=no-self-use
        """ Method 'PUT'
        """
        raise pyramid.httpexceptions.HTTPNotImplemented()


@apiramid.endpoint.Endpoint(path='/foo', request_method='GET')
def foo_get(context, request):
    """ Endpoint 'GET' 'foo'
    """
    dummy = (context, request)
    return pyramid.httpexceptions.HTTPOk()


@apiramid.endpoint.Endpoint(path='/foo', request_method='POST')
def foo_post(context, request):
    """ Endpoint 'POST' 'foo'
    """
    dummy = (context, request)
    return pyramid.httpexceptions.HTTPCreated()


@apiramid.endpoint.Endpoint(path='/item', request_method='GET')
class Item:  # pylint: disable=too-few-public-methods
    """ Endpoint 'item'
    """

    def __init__(self, context, request):
        dummy = context
        self.request = request
        return None

    def __call__(self):
        body = {
            'path': 'item',
            'method': 'GET',
        }
        result = pyramid.httpexceptions.HTTPOk(
            body=body,
        )
        return result


class TestResources(unittest.TestCase):
    """ Test cases for resources
    """

    def setUp(self):
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)
        self.config.scan('.')
        self.test_application = webtest.TestApp(self.config.make_wsgi_app())
        return None

    def tearDown(self):
        pyramid.testing.tearDown()
        return None

    def test_get_root(self):
        """ Test case for root endpoint
        """
        self.test_application.get('/', status=404)
        return None

    def test_get_foo(self):
        """ Test case for endpoint 'foo'
        """
        self.test_application.get('/v0.0/foo', status=200)
        return None

    def test_get_item(self):
        """ Test case for endpoint 'item'
        """
        self.test_application.get('/v0.0/item', status=200)
        return None

    def test_get_bar(self):
        """ Test case for endpoint 'bar'
        """
        self.test_application.get('/v0.0/bar/1', status=200)
        return None


# EOF
