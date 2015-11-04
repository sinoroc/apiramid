""" API module
"""


import jsonschema
import logging
import pyramid

from . import api
from . import i18n


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)

_ = i18n._


def validate_uri_parameter(parameter, value):
    """ Validate URI parameter.
    """
    if not value:
        if parameter.required:
            message = _("Required URI parameter {} is missing.").format(parameter.name)
            raise pyramid.httpexceptions.HTTPBadRequest(message)
    else:
        param_type = getattr(parameter, 'type', 'string')
        if param_type == 'integer' and not value.isdigit():
            message = _("URI parameter {} should be an integer.").format(parameter.name)
            raise pyramid.httpexceptions.HTTPBadRequest(message)
    return None


def validate_uri_parameters(request, resource):
    """ Validate URI parameters.
        Support of optional URI parameters seems incompatible with Pyramid's
        URL matching system.
        Extra work is required to support optional URI parameters.
    """
    uri_parameters = resource.uri_params or []
    for uri_parameter in uri_parameters:
        value = request.matchdict[uri_parameter.name]
        validate_uri_parameter(uri_parameter, value)
    return None


def validate_json_response(document, schema):
    """ Validate JSON response.
    """
    jsonschema.validate(document, schema)
    return None


def validate_response(request, resource, mime_type):
    api_util = request.registry.queryUtility(api.IApi)
    schema = api_util.find_schema(
        resource,
        200,
        mime_type,
    )
    validate_json_response(request.response.body, schema)
    return None


# EOF
