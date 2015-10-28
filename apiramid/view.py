""" API module
"""


import api
import json
import jsonschema
import logging
import pyramid

from .i18n import _


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)


def validate_uri_parameter(parameter, value):
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


def checkin(*args, **kwargs):
    """ Validate request.
    """
    dummy = kwargs
    request = args[1]

    api_util = request.registry.queryUtility(api.IApi)
    attr_name = api_util.request_endpoint_attribute
    endpoint = getattr(request, attr_name, None)
    resource = endpoint.dcmnt_resource

    checkin_uri_parameters(request, resource)

    return None


def checkin_uri_parameters(request, resource):
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


def validate_response(request, mime_type):
    api_util = request.registry.queryUtility(api.IApi)
    attr_name = api_util.request_endpoint_attribute
    endpoint = getattr(request, attr_name, None)
    schema = api_util.find_schema(
        endpoint.dcmnt_resource,
        200,
        mime_type,
    )
    validate_json_response(request.response.body, schema)
    return None


def checkout(*args, **kwargs):
    """ Validate response.
    """
    dummy = kwargs
    request = args[1]
    mime_type = 'application/json'
    if not isinstance(request.response, pyramid.httpexceptions.HTTPException):
        raise Exception("Response is not an HTTPException")
    validate_response(request, mime_type)
    return None


def render(*args, **kwargs):
    """ Render response.
    """
    dummy = kwargs
    request = args[1]
    renderer_name = 'json'
    result = pyramid.renderers.render_to_response(
        renderer_name=renderer_name,
        value=request.response.body,
        request=request
    )
    return result


# EOF
