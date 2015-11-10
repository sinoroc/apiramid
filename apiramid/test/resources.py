""" Test resources
"""


import apiramid
import logging
import pyramid


LOG = logging.getLogger(__name__)


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


# EOF
