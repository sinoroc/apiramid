""" Apiramid module
"""


import pyramid

from . import api
from . import endpoint
from . import views


MODULE_NAME = __name__


def includeme(config):
    """ Include the module in the Pyramid application.
    """

    document_path = config.registry.settings['{}.document'.format(MODULE_NAME)]

    definition = api.Api(document_path)
    config.registry.registerUtility(definition, api.IApi)

    config.add_directive('set_media_renderer', api.set_media_renderer)
    config.add_directive('add_deserializer', api.add_deserializer)
    config.add_directive('set_media_deserializer', api.set_media_deserializer)

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
