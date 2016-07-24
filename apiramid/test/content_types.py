""" Test content types
"""


import apiramid
import pyramid
import xmltodict


@apiramid.endpoint.EndpointDefaults(path='/capitalize', deserialize=True)
class Capitalize(object):

    def __init__(self, context, request):
        self.request = request
        return None

    def capitalize(self):
        text = self.request.dict_body.get('text', '')
        result = {
            'text': text.capitalize(),
        }
        return result

    @apiramid.endpoint.Endpoint(request_method='PUT')
    def put(self):
        result = self.capitalize()
        return pyramid.httpexceptions.HTTPOk(
            body=result,
        )


class XmlRendererFactory:

    MEDIA_TYPE = 'application/xml'

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system['request']
        response = request.response
        response.content_type = self.MEDIA_TYPE
        result = xmltodict.unparse(value)
        return result


class XmlDeserializerFactory:

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = xmltodict.parse(value)
        return result


class JsonDeserializerFactory:

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        result = system['request'].json_body
        return result


# EOF
