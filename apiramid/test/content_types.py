""" Test content types
"""


import apiramid
import pyramid


@apiramid.endpoint.EndpointDefaults(path='/capitalize')
class Capitalize(object):

    def __init__(self, context, request):
        self.request = request
        return None

    def capitalize(self):
        text = self.request.json_body.get('text', '')
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


# EOF
