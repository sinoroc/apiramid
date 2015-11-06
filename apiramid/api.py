""" API module
"""


import logging
import ramlfications
import urlparse
import zope.interface


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)


DEFAULT_MIME_RENDERERS = {
    'application/json': 'json',
    'text/plain': 'string',
}


class IApi(zope.interface.Interface):
    """ Interface for the API utility
    """
    pass


@zope.interface.implementer(IApi)
class Api(object):
    """ API utility
    """

    def __init__(self, document_path):
        self.raml = ramlfications.parse(document_path)
        self.base_path = urlparse.urlparse(self.raml.base_uri).path
        self.mime_renderers = DEFAULT_MIME_RENDERERS
        return None

    def find_resource(self, path, method):
        """ Find and return the corresponding resource in the document.
        """
        result = None
        for node in self.raml.resources:
            if node.path == path and node.method.upper() == method:
                result = node
                break
        return result

    def find_methods(self, path):
        """ Find methods allowed for this path.
        """
        result = []
        for node in self.raml.resources:
            if node.path == path:
                result.append(node.method.upper())
        return result

    def find_schema(self, resource, http_status_code, mime_type):
        """ Find and return the corresponding schema in the document.
            resource - class ramlfications.raml.ResourceNode
            http_status_code - int
            mime_type - string
        """
        result = {}
        responses = resource.responses or []
        for response in responses:
            if response.method == resource.method and response.code == http_status_code:
                for body in response.body:
                    if body.mime_type == mime_type:
                        result = body.schema
                        break
                break
        return result

    def set_mime_renderer(self, mime_type, renderer):
        """ Set the renderer for the MIME type.
        """
        self.mime_renderers[mime_type] = renderer
        return None

    def find_renderer_for_mime_type(self, mime_type):
        """ Find a renderer for this MIME type.
        """
        result = None
        for mime, renderer in self.mime_renderers.items():
            if mime == mime_type:
                result = renderer
                break
        return result


def set_mime_renderer(config, mime_type, renderer):
    """ Set the renderer for the MIME type.
    """
    api_util = config.registry.queryUtility(IApi)
    api_util.set_mime_renderer(mime_type, renderer)
    return None


# EOF
