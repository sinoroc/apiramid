""" API module
"""


import logging
import ramlfications
import urlparse
import zope


LOG = logging.getLogger(__name__)


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
        responses = resource.responses if resource.responses else []
        for response in responses:
            if response.method == resource.method and response.code == http_status_code:
                for body in response.body:
                    if body.mime_type == mime_type:
                        result = body.schema
                        break
                break
        LOG.error("Api.find_schema {}".format(result))
        return result


# EOF
