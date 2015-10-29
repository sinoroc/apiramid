""" Endpoint module
"""


import inspect
import logging
import pyramid
import venusian

from . import api
from . import i18n
from . import utils
from . import views


MODULE_NAME = __name__

LOG = logging.getLogger(MODULE_NAME)

_ = i18n._


class EndpointDefaults(object):
    """ Class decorator.
        Set defaults for methods decorated with ``Endpoint`` decorator.
    """

    ATTRIBUTE_NAME = '{}_endpoint_defaults'.format(MODULE_NAME)

    def __init__(self, **kwargs):
        """ Expected arguments: See Endpoint.__init__
        """
        self.endpoint_defaults = kwargs
        return None

    def __call__(self, decoratee):
        setattr(decoratee, self.ATTRIBUTE_NAME, self.endpoint_defaults)
        result = decoratee
        return result


class Endpoint(object):
    """ Decorator for function, method or class callable.
    """

    ROUTE_PREFIX = MODULE_NAME
    VENUSIAN_CATEGORY = MODULE_NAME
    VENUSIAN_SUBCATGEORY = MODULE_NAME

    routes = []

    def __init__(self, **kwargs):
        """ Expected keywords:
            ``method``
            ``path``
        """
        self.endpoint = kwargs
        # utility members
        self.api_util = None
        self.decoratee = None
        self.decoratee_class = None
        self.resource = None  # resource parsed from the API document
        self.venusian_info = None
        return None

    def __call__(self, decoratee):
        self.decoratee = decoratee
        self.venusian_info = venusian.attach(
            decoratee,
            self.callback,
            category=self.VENUSIAN_CATEGORY,
            name=self.VENUSIAN_SUBCATGEORY,
        )
        return decoratee

    def callback(self, scanner, dummy_name, obj):
        """ Venusian callback.
        """
        if self.venusian_info.scope == 'class':
            self.decoratee_class = obj
        config = scanner.config.with_package(self.venusian_info.module)
        self.set_defaults(getattr(obj, EndpointDefaults.ATTRIBUTE_NAME, {}))
        self.check()
        self.api_util = config.registry.queryUtility(api.IApi)
        resource = self.api_util.find_resource(
            self.endpoint['path'],
            self.endpoint['method'],
        )
        if resource:
            self.resource = resource
            self.add_endpoint(config)
        else:
            LOG.warning(_("Could not find resource."))
        return None

    def set_defaults(self, defaults):
        """ Set defaults from ``EntrypointDefaults`` if any.
            Already set values are not overwritten of course.
        """
        for key, value in defaults.items():
            if key not in self.endpoint:
                self.endpoint[key] = value
        return None

    @property
    def name_route(self):
        """ Name of the route for this endpoint.
        """
        result = '{prefix}_{path}'.format(
            prefix=self.ROUTE_PREFIX,
            path=self.endpoint['path'],
        )
        return result

    def check(self):
        """ Check the endpoint arguements.
        """
        if 'method' not in self.endpoint:
            comment = _("Endpoint has no method {}").format(self.endpoint)
            raise ValueError(comment)
        if 'path' not in self.endpoint:
            comment = _("Endpoint has no path {}").format(self.endpoint)
            raise ValueError(comment)
        return None

    def add_endpoint(self, config):
        """ Set an endpoint: add route if not available yet and add view.
        """
        self.add_route(config)
        self.add_view(config)
        return None

    def add_route(self, config):
        """ Add a Pyramid route if not added yet.
        """
        name = self.name_route
        if name not in self.routes:
            self.routes.append(name)
            path = '{base_path}{rel_path}'.format(
                base_path=self.api_util.base_path,
                rel_path=self.endpoint['path'],
            )
            config.add_route(name, path)
            self.add_options_view(config)
        return None

    def add_view(self, config):
        """ Add a Pyramid view.
        """
        config.add_view(
            view=self.view_callable,
            route_name=self.name_route,
            request_method=self.endpoint['method'],
        )
        return None

    def add_options_view(self, config):
        """ Add the Pyramid view for the OPTIONS method.
        """
        config.add_view(
            view=views.options_view,
            route_name=self.name_route,
            request_method='OPTIONS',
        )
        return None

    def view_callable(self, *args, **kwargs):
        """ The view callable.
        """
        request = args[1]
        self.checkin(request)
        request.response = self.run_user_view_callable(*args, **kwargs)
        self.checkout(request)
        result = self.render(request)
        return result

    def checkin(self, request):
        """ Validate request.
        """
        utils.validate_uri_parameters(request, self.resource)
        return None

    def run_user_view_callable(self, *args, **kwargs):
        """ Run the actual view callable decorated in the user application.
        """
        result = None
        if self.venusian_info.scope == 'class':
            # decoratee is a method
            view_callable = self.decoratee_class(*args, **kwargs)
            result = self.decoratee(view_callable)
        elif inspect.isclass(self.decoratee):
            # decoratee is a class callable
            view_callable = self.decoratee(*args, **kwargs)
            result = view_callable()
        elif inspect.isfunction(self.decoratee):
            # decoratee is a function
            result = self.decoratee(*args, **kwargs)
        else:
            raise Exception(_("Could not identify view callable."))
        return result

    def checkout(self, request):
        """ Validate response.
        """
        mime_type = 'application/json'
        if not isinstance(request.response, pyramid.httpexceptions.HTTPException):
            raise Exception(_("Response is not an HTTPException"))
        utils.validate_response(request, self.resource, mime_type)
        return None

    def render(self, request):
        """ Render response.
        """
        renderer_name = 'json'
        result = pyramid.renderers.render_to_response(
            renderer_name=renderer_name,
            value=request.response.body,
            request=request,
        )
        return result


# EOF
