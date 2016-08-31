""" API module
"""


import logging
import urllib

import pyramid
import ramlfications
import zope.interface


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)


DEFAULT_MEDIA_RENDERERS = {
    'application/json': 'json',
    'text/plain': 'string',
}


class IApi(zope.interface.Interface):  # pylint: disable=inherit-non-class
    """ Interface for the API utility
    """
    pass


@zope.interface.implementer(IApi)
class Api:
    """ API utility
    """

    def __init__(self, document_path):
        self.raml = ramlfications.parse(document_path)
        self.base_path = urllib.parse.urlparse(self.raml.base_uri).path
        self.media_renderers = DEFAULT_MEDIA_RENDERERS
        self.deserializers = {}
        self.media_deserializers = {}
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

    def find_schema(
            self,
            resource,
            http_status_code,
            media_type,
    ):  # pylint: disable=no-self-use
        """ Find and return the corresponding schema in the document.
            resource - class ramlfications.raml.ResourceNode
            http_status_code - int
            media_type - string
        """
        result = {}
        responses = resource.responses or []
        for response in responses:
            if (response.method == resource.method and
                    response.code == http_status_code):
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
        result = self.media_renderers.get(media_type, None)
        return result

    def add_deserializer(self, deserializer_handle, deserializer):
        """ Add a deserializer.
        """
        self.deserializers[deserializer_handle] = deserializer
        return None

    def set_media_deserializer(self, media_type, deserializer):
        """ Set the deserializer for this media type.
        """
        self.media_deserializers[media_type] = deserializer
        return None

    def find_media_deserializer(self, media_type):
        """ Find a desrializer for this media type.
        """
        result = self.media_deserializers.get(media_type, None)
        return result

    def deserialize(self, deserializer_name, value, request=None):
        """ Deserialize a value.
        """
        maybe_deserializer = self.deserializers[deserializer_name]
        resolver = pyramid.path.DottedNameResolver()
        deserializer = resolver.maybe_resolve(maybe_deserializer)
        info = {}
        system = {
            'request': request,
        }
        instance = deserializer(info)
        result = instance(value, system)
        return result


def set_media_renderer(config, media_type, renderer):
    """ Set the renderer for the media type.
    """
    api_util = config.registry.queryUtility(IApi)
    api_util.set_media_renderer(media_type, renderer)
    return None


def add_deserializer(config, deserializer_handle, deserializer):
    """ Add a deserializer.
    """
    api_util = config.registry.queryUtility(IApi)
    api_util.add_deserializer(deserializer_handle, deserializer)
    return None


def set_media_deserializer(config, media_type, deserializer):
    """ Set the renderer for the media type.
    """
    api_util = config.registry.queryUtility(IApi)
    api_util.set_media_deserializer(media_type, deserializer)
    return None


# EOF
