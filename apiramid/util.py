""" Utility belt
"""


import logging
import pyramid
import traceback

from . import api


LOG = logging.getLogger(__name__)


def options_view(request):
    """ Build a response for the OPTIONS method.
    """
    api_util = request.registry.queryUtility(api.IApi)
    route = request.matched_route.pattern
    path = route.replace(api_util.base_path, '')
    allowed_methods = api_util.find_methods(path)
    allow = ','.join(allowed_methods)
    result = pyramid.httpexceptions.HTTPNoContent(
        headers={
            'Allow': allow,
        },
    )
    return result


def build_http_exception_dict(http_exception, request):
    """ Build a renderable ``dict`` of the HTTP exception
    """
    request.response.status_code = http_exception.status_code
    return {
        'status_code': http_exception.status_code,
        'title': http_exception.title,
        'explanation': http_exception.explanation,
    }


def exception_view(exception, request):
    """ Render the view in case of HTTP exception.
        Build an internal server and do not leak internal details.
    """
    LOG.error("Exception {} '{}': {}".format(
        exception.__class__.__name__,
        str(exception),
        traceback.format_exc(),
    ))
    internal_exception = pyramid.httpexceptions.HTTPInternalServerError()
    return build_http_exception_dict(internal_exception, request)


def http_exception_view(exception, request):
    """ Render the view in case of HTTP exception. """
    LOG.error("HTTP exception {} '{}': {} -- {}".format(
        exception.code,
        exception.title,
        exception.detail,
        exception.comment,
    ))
    return build_http_exception_dict(exception, request)


# EOF
