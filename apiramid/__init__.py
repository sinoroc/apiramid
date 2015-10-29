""" Apiramid module
"""


import pyramid

from . import api
from . import endpoint


MODULE_NAME = __name__

__all__ = [
    'endpoint.EndpointDefaults',
    'endpoint.Endpoint',
]


def includeme(config):
    """ Include the module in the Pyramid application.
    """

    document_path = config.registry.settings['{}.document'.format(MODULE_NAME)]

    definition = api.Api(document_path)
    config.registry.registerUtility(definition, api.IApi)

    config.add_view(
        views.exception_view,
        context=Exception,
        renderer='json',
    )
    config.add_view(
        views.http_exception_view,
        context=pyramid.httpexceptions.HTTPException,
        renderer='json',
    )

    return None


# EOF
