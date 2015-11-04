""" Test resources
"""


import os
import unittest
import pyramid.testing
import webtest


PACKAGE_NAME = 'apiramid'
DOCUMENT = 'document.raml.yml'

DOCUMENT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    DOCUMENT,
)


class TestResources(unittest.TestCase):

    def setUp(self):
        settings = {
            '{}.document'.format(PACKAGE_NAME): DOCUMENT_PATH,
        }
        self.config = pyramid.testing.setUp(settings=settings)
        self.config.include(PACKAGE_NAME)
        self.config.scan('.resources')
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
