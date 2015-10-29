""" Apiramid module
"""


from . import endpoint


__all__ = [
    'endpoint.EndpointDefaults',
    'endpoint.Endpoint',
]


def includeme(config):
    """ Include the module in the Pyramid application.
    """
    import pyramid
    from . import api

    MODULE_NAME = __name__

    document_path = config.registry.settings['{}.document'.format(MODULE_NAME)]

    definition = api.Api(document_path)
    config.registry.registerUtility(definition, api.IApi)

    config.add_view(
        util.exception_view,
        context=Exception,
        renderer='json',
    )
    config.add_view(
        util.http_exception_view,
        context=pyramid.httpexceptions.HTTPException,
        renderer='json',
    )

    return None


# EOF
