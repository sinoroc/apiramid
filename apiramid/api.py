""" API module
"""


import logging
import ramlfications
import urlparse
import zope.interface


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)


DEFAULT_MEDIA_RENDERERS = {
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
        self.media_renderers = DEFAULT_MEDIA_RENDERERS
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

    def find_schema(self, resource, http_status_code, media_type):
        """ Find and return the corresponding schema in the document.
            resource - class ramlfications.raml.ResourceNode
            http_status_code - int
            media_type - string
        """
        result = {}
        responses = resource.responses or []
        for response in responses:
            if response.method == resource.method and response.code == http_status_code:
                for body in response.body:
                    if body.media_type == media_type:
                        result = body.schema
                        break
                break
        return result

    def set_media_renderer(self, media_type, renderer):
        """ Set the renderer for the media type.
        """
        self.media_renderers[media_type] = renderer
        return None

    def find_media_renderer(self, media_type):
        """ Find a renderer for this media type.
        """
        result = None
        for media, renderer in self.media_renderers.items():
            if media == media_type:
                result = renderer
                break
        return result


def set_media_renderer(config, media_type, renderer):
    """ Set the renderer for the media type.
    """
    api_util = config.registry.queryUtility(IApi)
    api_util.set_media_renderer(media_type, renderer)
    return None


# EOF
