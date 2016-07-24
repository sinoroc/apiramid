""" Test resources
"""


import logging
import os

import apiramid
import pyramid.testing
import unittest
import webtest


LOG = logging.getLogger(__name__)

PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


@pyramid.events.subscriber(pyramid.events.ApplicationCreated)
def show_routes_app(event):
    """ Log created routes.
    """
    introspector = event.app.registry.introspector
    introspectables = introspector.get_category('routes', [])
    routes = [route['introspectable']['pattern'] for route in introspectables]
    LOG.info("routes {}".format(routes))
    return None


@pyramid.events.subscriber(pyramid.events.NewRequest)
def log_request(event):
    """ Log incoming request.
    """
    LOG.info("--- {} {}".format(event.request.method, event.request.path_qs))
    return None


@apiramid.endpoint.EndpointDefaults(path='/bar/{id}')
class Bar(object):

    def __init__(self, context, request):
        self.request = request
        self.bar_id = int(request.matchdict['id'])
        return None

    @apiramid.endpoint.Endpoint(request_method='GET')
    def get(self):
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
    def post(self):
        raise pyramid.httpexceptions.HTTPNotImplemented()

    @apiramid.endpoint.Endpoint(request_method='PUT')
    def put(self):
        raise pyramid.httpexceptions.HTTPNotImplemented()


@apiramid.endpoint.Endpoint(path='/foo', request_method='GET')
def foo_get(context, request):
    return pyramid.httpexceptions.HTTPOk()


@apiramid.endpoint.Endpoint(path='/foo', request_method='POST')
def foo_post(context, request):
    return pyramid.httpexceptions.HTTPCreated()


@apiramid.endpoint.Endpoint(path='/item', request_method='GET')
class Item(object):

    def __init__(self, context, request):
        self.request = request

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
        response = self.test_application.get('/', status=404)
        return None

    def test_get_foo(self):
        response = self.test_application.get('/v0.0/foo', status=200)
        return None

    def test_get_item(self):
        response = self.test_application.get('/v0.0/item', status=200)
        return None

    def test_get_bar(self):
        response = self.test_application.get('/v0.0/bar/1', status=200)
        return None


# EOF
